Of course. Here is a complete README file, fully formatted in GitHub Markdown with headings, bullets, and icons. You can copy and paste this directly into a `README.md` file for your project.

-----

```markdown
# 🤖 WattOS AI Chatbot Platform

[![Status](https://img.shields.io/badge/status-active-success.svg)]()

A full-stack, RAG-enabled, and multi-user conversational AI platform built with FastAPI, LangGraph, and Streamlit. The application features a persistent PostgreSQL database for user and character management, a Qdrant vector store for document retrieval, and a professional, multi-tab user interface.

![WattOS AI Chatbot Screenshot](https://i.imgur.com/your-screenshot-url.png)
*(Suggestion: Replace this link with a URL to a screenshot of your final application UI)*

---

## ✨ Key Features

-   **🔐 Secure User Authentication:** Full registration and login system using JWT tokens.
-   **🗄️ Persistent PostgreSQL Database:** All user accounts and AI character profiles are stored permanently.
-   **📄 Document Upload & RAG:** Users can upload PDF documents, which are processed, vectorized, and stored in a **Qdrant** vector store. The AI then answers questions based on the content of these documents.
-   **🧠 Dynamic AI Agents & Personas:**
    -   **CRUD for Characters:** A full interface for creating, updating, and deleting different AI "Characters" with unique personalities.
    -   **LangGraph Visualization:** A dedicated tab to view interactive flowcharts of the AI's "brain," providing transparency and debuggability.
    -   **Smart Agent Selection:** The backend automatically selects the RAG agent if documents have been uploaded.
-   **🎙️ Advanced Chat Experience:**
    -   **Text & Audio Modes:** Users can choose between fast, text-only streaming and an audio-enabled mode with Text-to-Speech.
    -   **Selectable LLMs:** A dropdown menu allows for easy switching between different language models (e.g., GPT-4o, GPT-4 Turbo).
-   **🎨 Modern UI:** A clean, multi-tab user interface built with Streamlit, featuring a custom dark theme.

---

## 🛠️ Technology Stack

-   **Backend:** FastAPI, LangGraph, LangChain, SQLAlchemy
-   **Frontend:** Streamlit
-   **Databases:** PostgreSQL (user data), Qdrant (vector storage)
-   **AI Models:** OpenAI (GPT-4o, TTS-1), HuggingFace Embeddings
-   **Containerization:** Docker (for Qdrant)

---

## 📂 Project Structure

```

/
├── app/                  \# All backend FastAPI code
│   ├── main.py           \# Main FastAPI app & endpoints
│   ├── agent.py          \# LangGraph agent definitions
│   ├── auth.py           \# Security, JWT, password hashing
│   ├── characters.py     \# API for managing characters
│   ├── database.py       \# PostgreSQL connection
│   ├── models.py         \# SQLAlchemy database tables
│   ├── rag\_service.py    \# Document processing & Qdrant logic
│   ├── schemas.py        \# Pydantic data models
│   └── users.py          \# API for user registration & login
│
├── .streamlit/           \# Streamlit configuration
│   └── config.toml       \# Custom theme for the UI
│
├── .venv/                \# Python virtual environment
├── .env                  \# Environment variables (API keys, DB URL)
├── requirements.txt      \# Python dependencies
└── streamlit\_app.py      \# Frontend UI code

````

---

## 🚀 How to Run This Application

To run this project, you will need **three separate terminal windows** to run the Qdrant database, the backend server, and the frontend UI simultaneously.

### 1. Prerequisites

-   Python 3.10+
-   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
-   A PostgreSQL server running, with a database created (e.g., named `wattos_ai_db`).

### 2. Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-folder>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows
    .\.venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install all required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    -   Create a file named `.env` in the root of the project.
    -   Add your secret keys and database URL. It should look like this:
        ```env
        OPENAI_API_KEY="sk-..."
        DATABASE_URL="postgresql://<user>:<password>@<host>:<port>/wattos_ai_db"
        ```
    -   **Important:** Replace `<user>`, `<password>`, etc., with your actual PostgreSQL credentials.

5.  **Run the Backend Server (Terminal 1):**
    -   Open your first terminal and activate the virtual environment.
    -   Run the command:
        ```bash
        uvicorn app.main:app --reload
        ```
    -   The server will start on `http://localhost:8000`. Leave this terminal running.

### 3. Qdrant Database Setup

1.  **Open a second terminal window.**
2.  Run the command to start the Qdrant vector database using Docker:
    ```bash
    docker run -p 6333:6333 qdrant/qdrant
    ```
3.  Leave this terminal running in the background.

### 4. Frontend Setup

1.  **Open a third terminal window.**
2.  Navigate to the same project directory and activate the virtual environment.
3.  Run the command to start the Streamlit UI:
    ```bash
    streamlit run streamlit_app.py
    ```
4.  The application will automatically open in your web browser at `http://localhost:8501`.
````