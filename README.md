# 🚀 **MuneemAI -- Your Agentic Wealth Companion**

### **"India's First Proactive Financial Guardian"**

MuneemAI is not just another money management app---it's a **fully
autonomous financial agent** that works _for you_.\
While existing apps are passive tools, **MuneemAI is an active
guardian** that lives on WhatsApp, understands irregular income flows,
manages surplus intelligently, and shields users from risky decisions.

Built for India's gig workers, freelancers, and irregular earners,
MuneemAI helps users focus on earning while it handles the budgeting,
planning, and micro-investing.

---

## 🛡️ **What Makes MuneemAI Different?**

- **Proactive**, not reactive\
- **Autonomous**, not manually operated\
- **Risk-aware**, not blindly obedient\
- **Conversational**, running entirely on WhatsApp\
- **Designed for irregular income** (autos, gig workers, freelancers,
  agents, etc.)

---

## 🧠 **Architecture Overview**

MuneemAI is built on an **Agentic AI Architecture** where the LLM acts
as the "Brain" that controls specialized Python tools (the "Hands").

---

Component Technology Purpose

---

**The Brain** Google Gemini Flash / LangChain Understands user
intent, plans
actions, chooses safe
investment strategies

**The Tools** Python `@tool` functions Executes deposits,
investments, budget
calculations

**The Math** Pandas / NumPy (FinancialAggregator) Computes
volatility-adjusted
budgets via
Sustainable Variable
Budget Model

**The WhatsApp (Twilio) + FastAPI Receives messages,
Interface** responds to users,
triggers agent logic

**The Monitor** Streamlit Dashboard Real-time balances,
actions, charts,
crash simulation
button

---

---

## 🗂️ **Project Structure**

    muneemai/
    │
    ├── agent.py         # Core agent, LangChain logic, tools, volatility model
    ├── server.py        # FastAPI backend for Twilio WhatsApp webhook
    └── dashboard.py     # Streamlit dashboard for monitoring & actions

---

## 🛠️ **Setup Instructions**

### **Prerequisites**

- Python **3.10+**
- A Google API Key (Gemini)
- Optional: Twilio WhatsApp Sandbox

### **Install Dependencies**

```bash
pip install -r requirements.txt
```

Your requirements should include:

    langchain
    langchain-google-genai
    pandas
    numpy
    fastapi
    uvicorn
    streamlit
    python-dotenv
    plotly
    requests
    pydantic

### **Environment Setup**

Create a `.env` file:

    GOOGLE_API_KEY="your_key_here"

---

## 🚀 **How to Run the System**

MuneemAI requires **three terminal windows**.

---

### **1️⃣ Start Streamlit Dashboard**

```bash
streamlit run dashboard.py
```

Then click **"🔴 Reset System"** in the sidebar and complete onboarding
details.

---

### **2️⃣ Start the FastAPI Agent Backend**

```bash
uvicorn server:app --reload
```

---

### **3️⃣ (Optional) Start Twilio/ngrok Tunnel**

```bash
ssh -p 443 -R0:127.0.0.1:8000 a.pinggy.io
```


### ** Configure Twilio
Log in to your Twilio Console.

On the left sidebar, go to Messaging > Try it out > Send a WhatsApp message.

Click the small tab labeled Sandbox Settings (next to the "Sandbox" tab).

The Critical Field: Look for "When a message comes in".

Paste your Pinggy URL into that box.

🚨 ADD THE ENDPOINT: You MUST type /whatsapp at the end of the URL.

✅ Correct: https://r4nd0m-id.a.free.pinggy.link/whatsapp

❌ Wrong: https://r4nd0m-id.a.free.pinggy.link

Change the request method to HTTP POST.

Click Save.
---

## 🎬 **Demo Script (Magic Moments)**

### **✨ Scene 1 --- The Reactive Companion (Saving)**

The agent auto-invests after detecting income.

### **🛑 Scene 2 --- The Guardian (Safe Refusal)**

The agent refuses unsafe commands and reallocates safely.

### **⚡ Scene 3 --- The Proactive Shield (Autonomous Action)**

Triggered market crash → agent auto-rebalances instantly.

---

## 🤝 **Contributors**

- Faizal Ansari
- Omkar Gurav
- Vishal Verma
- Vinit Santani
