from math import log
from operator import is_
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.pregel.types import StateSnapshot

import logging
from datetime import datetime

# 以下のコードを参照のこと
# https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/review-tool-calls/

# ログの設定
def log_function_call(thread_id: str, function_name: str, message: str = None) -> None:
    if message:
        logging.info(f"Thread ID: {thread_id}, Function: {function_name}, Message: {message}")
    else:
        logging.info(f"Thread ID: {thread_id}, Function: {function_name}")
@tool
def weather_search(city: str) -> str:
    """Search for the weather"""
    return "Sunny!"


class HumanInTheLoopAgentState(MessagesState):
    """Simple state."""


class HumanInTheLoopAgent:
    def __init__(self) -> None:
        builder = StateGraph(HumanInTheLoopAgentState)
        builder.add_node("call_llm", self._call_llm)
        builder.add_node("run_tool", self._run_tool)
        builder.add_node("human_review_node", self._human_review_node)
        builder.add_edge(START, "call_llm")
        builder.add_conditional_edges("call_llm", self._route_after_llm)
        builder.add_conditional_edges("human_review_node", self._route_after_human)
        builder.add_edge("run_tool", "call_llm")

        memory = MemorySaver()

        self.graph = builder.compile(
            checkpointer=memory,
            interrupt_before=["human_review_node"],
        )

    def _call_llm(self, state: dict) -> dict:
        log_function_call(state.get("thread_id", "unknown"), "_call_llm")
        model = ChatOpenAI(model="gpt-4o-mini").bind_tools([weather_search])
        return {"messages": [model.invoke(state["messages"])]}

    def _human_review_node(self, state: dict) -> None:
        log_function_call(state.get("thread_id", "unknown"), "_human_review_node")

    def _run_tool(self, state: dict) -> dict:
        log_function_call(state.get("thread_id", "unknown"), "_run_tool")
        new_messages = []
        tools = {"weather_search": weather_search}
        tool_calls = state["messages"][-1].tool_calls
        for tool_call in tool_calls:
            tool = tools[tool_call["name"]]
            result = tool.invoke(tool_call["args"])
            new_messages.append(
                {
                    "role": "tool",
                    "name": tool_call["name"],
                    "content": result,
                    "tool_call_id": tool_call["id"],
                }
            )
        return {"messages": new_messages}

    def _route_after_llm(self, state: dict) -> Literal[END, "human_review_node"]:
        log_function_call(state.get("thread_id", "unknown"), "_route_after_llm")
        if len(state["messages"][-1].tool_calls) == 0:
            return END
        else:
            return "human_review_node"

    def _route_after_human(self, state: dict) -> Literal["run_tool", "call_llm"]:
        log_function_call(state.get("thread_id", "unknown"), "_route_after_human")
        if isinstance(state["messages"][-1], AIMessage):
            return "run_tool"
        else:
            return "call_llm"

    def handle_human_message(self, human_message: str, thread_id: str) -> None:
        # 承認待ちの状態でhuman_messageが送信されるのは、ツールの呼び出しを修正したい状況
        # そのため、次がhuman_review_nodeの場合、ツールの呼び出しが失敗したことをStateに追加
        # 参考: https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/review-tool-calls/#give-feedback-to-a-tool-call
        is_next_human_review_node = self.is_next_human_review_node(thread_id)
        log_function_call(thread_id, "handle_human_message", str(is_next_human_review_node))
        if is_next_human_review_node:
            self._handle_tool_call_rejection(thread_id)
    
        for _ in self.graph.stream(
            input={"messages": [HumanMessage(content=human_message)]},
            config=self._config(thread_id),
            stream_mode="values",
        ):
            pass
    
    def _handle_tool_call_rejection(self, thread_id: str) -> None:
        log_function_call(thread_id, "_handle_tool_call_rejection")
        last_message = self.get_messages(thread_id)[-1]
        tool_reject_message = ToolMessage(
            content="Tool call rejected",
            status="error",
            name=last_message.tool_calls[0]["name"],
            tool_call_id=last_message.tool_calls[0]["id"],
        )
        self.graph.update_state(
            config=self._config(thread_id),
            values={"messages": [tool_reject_message]},
            as_node="human_review_node",
        )

    def handle_approve(self, thread_id: str) -> None:
        log_function_call(thread_id, "handle_approve")
        for _ in self.graph.stream(
            input=None,
            config=self._config(thread_id),
            stream_mode="values",
        ):
            pass

    def get_messages(self, thread_id: str) -> Any:
        log_function_call(thread_id, "get_messages")
        return self._get_state(thread_id).values["messages"]  # noqa: PD011

    def is_next_human_review_node(self, thread_id: str) -> bool:
        """
        is_next_human_review_node 関数は、
        特定のスレッドが次に「人間によるレビュー」ノードに進むかどうかを判定するためのメソッドです。
        この関数は、thread_id という文字列を引数に取り、ブール値を返します。
        """
        graph_next = self._get_state(thread_id).next
        result = len(graph_next) != 0 and graph_next[0] == "human_review_node"
        log_function_call(thread_id, "is_next_human_review_node", message=str(result))
        return result

    def _get_state(self, thread_id: str) -> StateSnapshot:
        # log_function_call(thread_id, "_get_state")
        return self.graph.get_state(config=self._config(thread_id))

    def _config(self, thread_id: str) -> RunnableConfig:
        # log_function_call(thread_id, "_config")
        return {"configurable": {"thread_id": thread_id}}

    def mermaid_png(self) -> bytes:
        # log_function_call("unknown", "mermaid_png")
        return self.graph.get_graph().draw_mermaid_png()
