# 📜 RCU Heritage AI Chatbot – Image & Knowledge-Based Retrieval System

An AI-powered multimodal heritage assistant built for **Royal Commission for AlUla (RCU)** that enables:

* 📖 Knowledge-based search over heritage documents (PDF)
* 🖼 Image-based object recognition & explanation
* 🤖 Agentic AI orchestration using tools
* 🔎 Vector search with ChromaDB
* 💬 Integration-ready with Microsoft 365 Agents

---

# 📌 Overview

This project demonstrates an **Agentic AI-powered Heritage Chatbot** capable of:

1. Retrieving information from RCU heritage documents.
2. Searching similar artifacts based on uploaded images.
3. Explaining historical context using LLM + RAG.
4. Running as a Microsoft 365 Agents or FastAPI-based backend service.
5. Integrating with Microsoft Agents SDK / Omnichannel.

The system uses:

* **LangChain**
* **ChromaDB**
* **Groq LLM**
* **Microsoft 365 Agents**
* **Agent + Tools architecture**

---

Perfect — add the following section in your `README.md` under a new heading like:

---

## 📚 Data Source Attribution

The PDF document used in this repository:

**“AlUla Collections – 100 Objects”**

has been sourced from the official Royal Commission for AlUla (RCU) Open Data Library:

🔗 [https://www.rcu.gov.sa/en/open-data-library/alula-collections-100-objects](https://www.rcu.gov.sa/en/open-data-library/alula-collections-100-objects)

This material is publicly available through RCU’s Open Data platform and is used in this repository strictly for demonstration and research purposes to showcase AI-powered heritage knowledge retrieval and image-based search capabilities.

All intellectual property rights and ownership of the original content remain with the Royal Commission for AlUla (RCU).

---


# 🏛 Architecture Overview

## 1️⃣ High-Level Flow

```
User → Bot Channel (LiveChat) →              Agent
                                               ↓
                                ┌──────────────┴──────────────┐
                                │                             │
                         PDF Knowledge RAG              Image Search Tool
                                │                             │
                          ChromaDB Vector Store        Embedding + Retrieval
                                │                             │
                                └──────────────┬──────────────┘
                                               ↓
                                       Structured Response
                                               ↓
                                           User Reply
```

---

# 🌍 Open Source–First Architecture

This project is intentionally designed using **open-source technologies and standards**, ensuring:

* ✅ No vendor lock-in
* ✅ Full transparency of components
* ✅ Extensibility and customization
* ✅ Enterprise portability (on-prem / cloud / hybrid)
* ✅ Cost optimization

All core architectural layers leverage OSS frameworks and libraries.

---

# 🧩 Open Source Technology Stack

Below is a breakdown of the open-source components used in this solution:

| Layer            | Technology                                  | Open Source Status |
| ---------------- | ------------------------------------------- | ------------------ |
| API Framework    | **FastAPI**                                 | Open Source (MIT)  |
| AI Orchestration | **LangChain**                               | Open Source        |
| Vector Database  | **ChromaDB**                                | Open Source        |
| Data Processing  | **Python**                                  | Open Source        |
| Embeddings       | **hugging face** embedding models           | Open               |
| Notebook         | **Jupyter Notebook**                        | Open Source        |
| Web Server       | **Uvicorn**                                 | Open Source        |
| Dependency Mgmt  | **pip / venv**                              | Open Source        |

> The architecture remains fully portable and can run in any standard Python environment without proprietary infrastructure requirements.

---

# 📂 Repository Structure

```
rcu_heritage_chatbot_demo/
│
├── app/
│   ├── agents.py              # Agent definitions & orchestration logic
│   ├── app.py                 # Bot message handling logic
│   ├── llm_model.py           # Groq LLM configuration
│   ├── response_schemas.py    # Pydantic response schemas
│   ├── tools.py               # Image search & RAG tools
│   ├── main.py                # app entry
│   ├── start_server.py        # Local server bootstrap
│   └── __init__.py
│
├── data/
│   ├── alula-collections-100-objects.pdf
│   ├── chroma_langchain_db/   # Vector DB persistence
│   ├── uploaded_images/       # Uploaded images
│   └── output/
│       ├── images/            # pdf containes images    
│       ├── langchain_docs.json
│       └── objects.json
│
├── notebooks/
│   └── data_ingestion_to_chromadb.ipynb  # PDF ingestion workflow
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

# 🧠 Core Components Explained

---

## 1️⃣ LLM Layer – `llm_model.py`

Configures Groq LLM used by the agent.

Responsible for:

* Response generation
* Tool calling decisions
* Structured output formatting

---

## 2️⃣ Tools – `tools.py`

Implements:

### 🔎 Knowledge RAG Tool

* Uses ChromaDB
* Retrieves relevant document chunks
* Returns contextual explanation

### 🖼 Image Search Tool

* Accepts local image path
* Generates embeddings
* Retrieves similar artifacts
* Produces explanation

---

## 3️⃣ Agent – `agents.py`

Defines:

* Tool-enabled AI agent
* Structured JSON output
* Tool routing logic
* Controlled response schema

---

## 4️⃣ Bot Handling – `app.py`

Handles:

* Incoming messages
* Image uploads
* File download
* Agent invocation
* Response sending

---

## 5️⃣ Vector Database – ChromaDB

Location:

```
data/chroma_langchain_db/
```

Stores:

* Embedded PDF chunks
* Artifact embeddings
* Metadata

Persistent across sessions.

---

# 🚀 How to Run (Step-by-Step)

---

# ✅ Step 1: Clone Repository

```bash
git clone https://github.com/MusaddiqueHussainLabs/rcu_heritage_chatbot_demo.git
cd rcu_heritage_chatbot_demo
```

---

# ✅ Step 2: Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

# ✅ Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ✅ Step 4: Set Environment Variables

Create `.env` file:

```
GROQ_API_KEY=your_groq_api_key
```

If using Microsoft Bot Framework:

```
MICROSOFT_APP_ID=your_app_id
MICROSOFT_APP_PASSWORD=your_password
```

---

# ✅ Step 5: Start Server

```bash
python app/start_server.py
```

Or:

```bash
uvicorn app.main:app --reload --port 8000
```

Server runs at:

```
http://localhost:8000
```

---

# 🖼 Image Upload Workflow

When user uploads image:

1. Bot receives attachment
2. Image saved to:

```
data/uploaded_images/
```

3. Agent invoked with:

```
search_by_image_and_explain(image_path=...)
```

4. Tool retrieves similar artifacts
5. LLM generates explanation
6. Response sent to user

---

# 📖 How to Ingest New PDF Data

Open notebook:

```
notebooks/data_ingestion_to_chromadb.ipynb
```

Steps:

1. Load PDF
2. Chunk text
3. Generate embeddings
4. Store in ChromaDB

After ingestion:

* Restart server
* New data searchable immediately

---

# 🧩 How to Utilize This Repo (RCU Usage Guide)

This repository can be used in 3 ways:

---

## 1️⃣ Reference Implementation

RCU can:

* Review architecture
* Extend tools
* Integrate with enterprise channels
* Deploy to Azure

---

## 2️⃣ Production Deployment

Recommended Production Setup:

* Azure App Service
* Azure Container Apps
* Azure OpenAI (optional replacement for Groq)
* Azure Cosmos DB (optional vector DB alternative)

---

## 3️⃣ Extension Use Cases

Can be extended to:

* Multi-language Arabic support
* Audio-based artifact recognition
* Museum kiosk integration
* Visitor mobile app integration
* Guided tour AI assistant

---

# 🔐 Security Considerations

* Never expose raw tool traces
* Limit response size
* Sanitize LLM output
* Secure API keys in Key Vault
* Use HTTPS in production

---

# ⚙ Performance Optimization

* Limit response length (<4000 chars)
* Use persistent ChromaDB
* Cache embeddings
* Send immediate acknowledgement to avoid channel timeout

---

# 📊 Technology Stack

| Layer           | Technology           |
| --------------- | -------------------- |
| Agent Framework | LangChain            |
| LLM             | Groq                 |
| Vector DB       | ChromaDB             |
| Bot Integration | Microsoft Agents SDK |
| Storage         | Local filesystem     |
| Notebook        | Jupyter              |

---

# 🏗 Production Deployment Recommendation for RCU

For enterprise readiness:

1. Dockerize application
2. Deploy to Azure Kubernetes Service
3. Use Azure Key Vault
4. Replace local storage with Azure Blob
5. Use Azure Monitor
6. Add centralized logging

---

# 🎯 Key Capabilities Delivered

✔ Multimodal Search
✔ Agentic Tool Routing
✔ Vector-Based Retrieval
✔ Structured Response Schema
✔ Enterprise-Ready Architecture
✔ LiveChat Integration

---

# 🔮 Future Roadmap

* Arabic LLM support
* Multi-agent supervisor routing
* Fine-tuned heritage domain model
* On-prem deployment option
* Vision transformer integration

---

# 📞 Maintainer

**Musaddique Hussain Labs**
AI Architect & Agentic AI Specialist

GitHub:
[https://github.com/MusaddiqueHussainLabs](https://github.com/MusaddiqueHussainLabs)

---

# 📄 License

This project is licensed under the MIT License.

---

# 🏁 Final Notes for RCU

This repository demonstrates a scalable foundation for:

> "AI-Powered Digital Heritage Intelligence Platform"

It can serve as:

* A reference prototype
* A production-ready base
* A foundation for enterprise AI transformation