# KnoBot: Your Personal Document Chatbot

KnoBot is a full-stack AI application that lets you upload your private documents (like PDFs) and then ask questions about them. It's built with a secure FastAPI backend and an interactive Streamlit frontend.

![KnoBot Application Screenshot](https://i.imgur.com/your-screenshot-url.png)
*(Suggestion: Replace this with a real screenshot of your app!)*

---

## ✨ Features

* **Secure Login:** Register and log in to a persistent PostgreSQL database.
* **Document Q&A:** Upload your PDFs and ask questions. The AI will answer *only* based on your documents.
* **AI Personas:** Create different AI "Characters" with unique personalities.
* **Text & Audio:** Get responses as streaming text or listen to them with text-to-speech.

---

## 🚀 How to Run (Quick Start)

You need three services running at the same time:
1.  **Qdrant Database (for documents)**
2.  **Backend Server (for the AI logic)**
3.  **Frontend App (for the UI)**

### 1. Prerequisites

* Python 3.10+
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* PostgreSQL

### 2. Setup

1.  **Clone & Install:**
    ```bash
    git clone [https://github.com/mnabeelasad/KnoBot.git](https://github.com/mnabeelasad/KnoBot.git)
    cd KnoBot
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Configure `.env` File:**
    -   Create a file named `.env` in the project folder.
    -   Add your API key and database URL:
        ```env
        OPENAI_API_KEY="sk-..."
        DATABASE_URL="postgresql://<user>:<password>@localhost:5432/wattos_ai_db"
        ```

### 3. Run the Application

1.  **Terminal 1: Start Qdrant**
    ```bash
    docker run -p 6333:6333 qdrant/qdrant
    ```

2.  **Terminal 2: Start Backend**
    ```bash
    uvicorn app.main:app --reload
    ```

3.  **Terminal 3: Start Frontend**
    ```bash
    streamlit run streamlit_app.py
    ```

Your application is now running at **`http://localhost:8501`**.
