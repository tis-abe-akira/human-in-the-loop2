import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const ChatMessage = ({ message }) => (
  <div className={`message ${message.type}`}>
    <p>{message.content}</p>
  </div>
);

const App = () => {
  const [threadId, setThreadId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isWaitingForApproval, setIsWaitingForApproval] = useState(false);

  useEffect(() => {
    const startConversation = async () => {
      try {
        const response = await axios.post(`${API_BASE_URL}/start_conversation`);
        setThreadId(response.data.thread_id);
      } catch (error) {
        console.error('Failed to start conversation:', error);
      }
    };

    startConversation();
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    try {
      const response = await axios.post(`${API_BASE_URL}/send_message/${threadId}`, {
        message: inputMessage
      });
      setMessages(response.data.messages);
      setIsWaitingForApproval(response.data.is_waiting_for_approval);
      setInputMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleApprove = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/approve/${threadId}`);
      setMessages(response.data.messages);
      setIsWaitingForApproval(response.data.is_waiting_for_approval);
    } catch (error) {
      console.error('Failed to approve:', error);
    }
  };

  return (
    <div className="chat-container">
      <h2>LangGraph Human-in-the-loop Chat</h2>
      {threadId && (
        <div className="thread-id">
          <p>Thread ID: {threadId}</p>
        </div>
      )}
      <div className="messages-container">
        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
      {isWaitingForApproval && (
        <div className="approval-container">
          <p>Waiting for approval...</p>
          <button onClick={handleApprove}>Approve</button>
        </div>
      )}
    </div>
  );
};

export default App;
