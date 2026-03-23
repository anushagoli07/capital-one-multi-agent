# 🏦 Capital One Multi-Agent Financial Assistant

An enterprise-grade, agentic RAG assistant designed to analyze financial documents and provide safe, explainable answers.

## 🚀 Key Features
- **Multi-Agent Architecture**: Uses `LangGraph` to orchestrate a **Planner Agent**, a **Reasoning Agent** (with FAISS search), and a **Guardrail Agent**.
- **Agentic Workflows**: Decisions are made dynamically based on user intent.
- **Security & Safety**: Integrated PII detection and Nemo Guardrails for hallucination prevention.
- **Trace Visualization**: Real-time "thought process" logs visible in the Streamlit UI.
- **Monitoring**: Out-of-the-box integration with the [AI Deployment Debugger](https://github.com/anushagoli07/ai-deployment-debugger).

## 🛠️ Tech Stack
- **Framework**: LangGraph, FastAPI, Streamlit
- **LLM**: OpenAI GPT-4o-mini
- **Vector DB**: FAISS
- **Security**: Nemo Guardrails, Presidio

## 📦 Installation
1. Clone the repo:
   ```bash
   git clone https://github.com/anushagoli07/capital-one-multi-agent.git
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up `.env`:
   ```env
   OPENAI_API_KEY=your_key
   AWS_ACCESS_KEY_ID=your_id
   AWS_SECRET_ACCESS_KEY=your_secret
   ```

## 🏃 Running the App
1. **Start Backend**:
   ```bash
   uvicorn api.main:app --port 8000
   ```
2. **Start Frontend**:
   ```bash
   streamlit run ui/streamlit_app.py
   ```

## 🛡️ Live Monitoring
This project is connected to a dedicated **AI Debugger**. Every query you make is tracked for latency, cost, and error classification.
