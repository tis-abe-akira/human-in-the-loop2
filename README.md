# LangGraph Human-in-the-loop Chat Application

This project demonstrates a human-in-the-loop chat application using LangGraph, implemented with a FastAPI backend and a React frontend. It showcases how to integrate human approval into an AI-driven conversation flow.

## Features

- AI-driven conversation using LangGraph and OpenAI's GPT models
- Human-in-the-loop functionality for approving AI actions
- FastAPI backend for handling chat logic and API endpoints
- React frontend for user interaction
- Real-time updates and approval requests

## Project Structure

The project is divided into two main parts:

1. Backend (FastAPI + Poetry)
2. Frontend (React + Vite)

### Backend

The backend is responsible for:
- Managing the conversation flow
- Integrating with LangGraph and OpenAI
- Providing API endpoints for the frontend

### Frontend

The frontend provides:
- A user-friendly interface for the chat application
- Real-time updates of the conversation
- Buttons for sending messages and approving AI actions

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm 6+
- Poetry
- OpenAI API key

## Setup

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd langchain-hitl-backend
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Create a `.env` file in the backend directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. Run the backend server:
   ```
   poetry run uvicorn main:app --reload
   ```

The backend will be available at `http://localhost:8000`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd langchain-hitl-frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`.

## Usage

1. Open your web browser and go to `http://localhost:5173`.
2. Start a conversation by typing a message in the input field and clicking "Send".
3. The AI will respond and may request approval for certain actions.
4. When prompted, review the AI's proposed action and click "Approve" if you agree.
5. Continue the conversation as desired.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [LangChain](https://github.com/hwchase17/langchain) for providing the LangGraph framework
- [OpenAI](https://openai.com/) for their GPT models
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend library
