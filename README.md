# Inzurio Healthcare System

Inzurio is a maximalist health tracking and LLM-powered lab report intelligence agent. It allows users to upload their medical lab reports, automatically extracts critical health data using large language models, and lets users converse with an AI agent to analyze their health history.

## Features

- **Automated Data Extraction:** Upload PDF or image-based lab reports, and the system intelligently extracts test results, reference ranges, and flags using the `openrouter/free` endpoint.
- **AI Agent Chat:** Converse with your medical data. Ask the agent for your latest test results, historical trends, or out-of-range indicators.
- **SQLite Database:** Local persistence of extracted lab data.
- **FastAPI Backend:** Fast and modern Python backend.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, SQLite
- **LLM Integration:** OpenRouter (`openrouter/free`), OpenAI Python SDK
- **File Parsing:** PyMuPDF (fitz)
- **Frontend:** HTML, Vanilla CSS, JS

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DeepBartaria/Inzurio-Healthcare-System.git
   cd Inzurio-Healthcare-System
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your OpenRouter API key:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

## Running Locally

To start the FastAPI application:

```bash
uvicorn main:app --reload
```

Then, open your browser and navigate to `http://127.0.0.1:8000` to access the Inzurio dashboard.

## Deployment Notes (Vercel)

A `vercel.json` file is included for deploying to Vercel Serverless Functions. Please note that Vercel uses an ephemeral filesystem, meaning local SQLite database writes and local file uploads (`/uploads`) will not persist across requests. For production deployment, you will need to migrate to a remote database (e.g., Supabase, Neon) and remote storage (e.g., AWS S3).
