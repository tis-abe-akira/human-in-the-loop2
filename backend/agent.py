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
    """関数呼び出しをログに記録するヘルパー関数"""
    if message:
        logging.info(f"Thread ID: {thread_id}, Function: {function_name}, Message: {message}")
    else:
        logging.info(f"Thread ID: {thread_id}, Function: {function_name}")

@tool
def weather_search(city: str) -> str:
    """指定された都市の天気を検索するツール関数"""
    return "Sunny!"

class HumanInTheLoopAgentState(MessagesState):
    """エージェントの状態を表すシンプルなクラス"""

class HumanInTheLoopAgent:
    def __init__(self) -> None:
        """エージェントの初期化メソッド"""
        builder = StateGraph(HumanInTheLoopAgentState)
        # ノードの追加
        builder.add_node("call_llm", self._call_llm)
        builder.add_node("run_tool", self._run_tool)
        builder.add_node("human_review_node", self._human_review_node)
        # エッジの追加
        builder.add_edge(START, "call_llm")
        builder.add_conditional_edges("call_llm", self._route_after_llm)
        builder.add_conditional_edges("human_review_node", self._route_after_human)
        builder.add_edge("run_tool", "call_llm")

        memory = MemorySaver()

        # グラフのコンパイル
        self.graph = builder.compile(
            checkpointer=memory,
            interrupt_before=["human_review_node"],
        )

    def _call_llm(self, state: dict) -> dict:
        """LLM（大規模言語モデル）を呼び出すメソッド"""
        log_function_call(state.get("thread_id", "unknown"), "_call_llm")
        model = ChatOpenAI(model="gpt-4o-mini").bind_tools([weather_search])
        return {"messages": [model.invoke(state["messages"])]}

    def _human_review_node(self, state: dict) -> None:
        """人間によるレビューを行うノード"""
        log_function_call(state.get("thread_id", "unknown"), "_human_review_node")

    def _run_tool(self, state: dict) -> dict:
        """ツールを実行するノード"""
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
        """LLM呼び出し後のルーティングを行うメソッド"""
        log_function_call(state.get("thread_id", "unknown"), "_route_after_llm")
        if len(state["messages"][-1].tool_calls) == 0:
            return END
        else:
            return "human_review_node"

    def _route_after_human(self, state: dict) -> Literal["run_tool", "call_llm"]:
        """人間によるレビュー後のルーティングを行うメソッド"""
        log_function_call(state.get("thread_id", "unknown"), "_route_after_human")
        if isinstance(state["messages"][-1], AIMessage):
            return "run_tool"
        else:
            return "call_llm"

    def handle_human_message(self, human_message: str, thread_id: str) -> None:
        """人間からのメッセージを処理するメソッド"""
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
        """ツール呼び出しの拒否を処理するメソッド"""
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
        """承認を処理するメソッド"""
        log_function_call(thread_id, "handle_approve")
        for _ in self.graph.stream(
            input=None,
            config=self._config(thread_id),
            stream_mode="values",
        ):
            pass

    def get_messages(self, thread_id: str) -> Any:
        """指定されたスレッドのメッセージを取得するメソッド"""
        log_function_call(thread_id, "get_messages")
        return self._get_state(thread_id).values["messages"]  # noqa: PD011

    def is_next_human_review_node(self, thread_id: str) -> bool:
        """次のノードが人間によるレビューかどうかを判定するメソッド"""
        graph_next = self._get_state(thread_id).next
        result = len(graph_next) != 0 and graph_next[0] == "human_review_node"
        log_function_call(thread_id, "is_next_human_review_node", message=str(result))
        return result

    def _get_state(self, thread_id: str) -> StateSnapshot:
        """指定されたスレッドの状態を取得するメソッド"""
        return self.graph.get_state(config=self._config(thread_id))

    def _config(self, thread_id: str) -> RunnableConfig:
        """指定されたスレッドの設定を取得するメソッド"""
        return {"configurable": {"thread_id": thread_id}}

    def mermaid_png(self) -> bytes:
        """グラフのMermaid形式のPNG画像を生成するメソッド"""
        return self.graph.get_graph().draw_mermaid_png()
