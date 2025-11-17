# Healthcare Knowledge Assistant: RAG-Based AI Chatbot

A production-ready **Retrieval-Augmented Generation (RAG)** powered healthcare knowledge assistant that combines large language models with vector databases to provide intelligent, context-aware responses to hospital-related queries. Built with FastAPI, LangChain, and Chroma, this system demonstrates advanced AI/ML capabilities with real-world applications in healthcare information management.

**Author:** Abhishek Suwalka  
**Email:** suwalkabhishek@gmail.com  
**LinkedIn:** [AbhishekSuwalka](http://linkedin.com/in/AbhishekSuwalka)

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Installation & Setup](#installation--setup)
6. [Quick Start Guide](#quick-start-guide)
7. [API Endpoints Documentation](#api-endpoints-documentation)
8. [How the Bot Works](#how-the-bot-works)
9. [Safety & Relevance Mechanisms](#safety--relevance-mechanisms)
10. [Configuration](#configuration)
11. [Deployment](#deployment)
12. [Testing & Evaluation](#testing--evaluation)
13. [Future Enhancements](#future-enhancements)
14. [License & Support](#license--support)

---

## 🎯 Project Overview

The **Healthcare Knowledge Assistant** is an intelligent conversational AI system designed to answer questions about hospital policies, procedures, billing, and general healthcare information. It uses **Retrieval-Augmented Generation (RAG)**, a cutting-edge technique that combines:

- **Document Retrieval:** Vector similarity search to find relevant documents from a knowledge base
- **Large Language Models:** State-of-the-art LLMs (Gemini, OpenAI) for generating contextually accurate responses
- **Safety Controls:** Built-in mechanisms to prevent providing medical diagnoses or medication recommendations
- **Role-Based Prompting:** Context-aware responses tailored to different user roles (doctors, receptionists, billing staff, general users)

This architecture ensures **accurate, grounded responses** without hallucinations, as the system only generates answers based on indexed documents.

### Use Cases

✅ **Hospital Reception:** Visiting hours, admission procedures, appointment scheduling  
✅ **Patient Information:** Billing inquiries, insurance details, facility information  
✅ **Staff Support:** Hospital policies, procedures, departmental information  
✅ **Medical Professionals:** Evidence-based policy and procedure references  

---

## ✨ Key Features

### 🧠 Advanced RAG Implementation
- **Multi-LLM Support:** Seamlessly switch between Google Gemini, OpenAI, and Azure OpenAI
- **Multi-Embedding Support:** Support for Gemini, OpenAI, and Azure embeddings
- **Semantic Search:** Vector-based similarity search for precise document retrieval
- **Chunk Optimization:** Intelligent document chunking with configurable overlap for context preservation

### 🔐 Safety & Guardrails
- **No Medical Diagnosis:** System explicitly refuses to provide medical diagnoses
- **No Medication Recommendations:** Prevents prescribing or dosage recommendations
- **Context-Only Responses:** Answers strictly based on indexed documents; clearly indicates when information is unavailable
- **Emergency Directions:** Automatically directs users to emergency services when appropriate
- **Medical Disclaimer:** Every response includes a safety disclaimer

### 👥 Role-Based Intelligence
- **Doctor Mode:** Detailed, professional responses for healthcare professionals
- **Receptionist Mode:** Clear, simple information for front-desk staff
- **Billing Mode:** Precise financial information and payment options
- **General Mode:** Patient-friendly, easy-to-understand information

### 🛠️ Extensible Tool System
- **MCP Tool Registry:** Modular tool architecture for extending functionality
- **Available Tools:**
  - `get_current_datetime`: Current time, date, and timezone info
  - `calculate_age`: Calculate patient age from birthdate
  - `get_working_hours`: Retrieve hospital department hours
  - `search_internal_docs`: Search hospital knowledge base
  - `web_search`: Retrieve external health information

### 📊 Production-Ready Architecture
- **Async FastAPI:** High-performance REST API with async/await support
- **Comprehensive Logging:** Detailed operation tracking for debugging and monitoring
- **Error Handling:** Graceful error management with informative error responses
- **CORS Support:** Cross-origin resource sharing for frontend integration
- **Health Checks:** System status monitoring and vector database verification

---

## 🛠️ Technology Stack

### Backend Framework
- **FastAPI** (0.104+) - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server for production deployment
- **Pydantic v2** - Data validation and serialization

### LLM & Embeddings
- **LangChain** - Framework for building LLM applications
- **Google Gemini API** (Primary) - State-of-the-art multimodal LLM
- **OpenAI API** (Fallback) - GPT-4/GPT-3.5 for backup support
- **Azure OpenAI** (Optional) - Enterprise Azure integration

### Vector Database & Retrieval
- **Chroma** - Fast, effective vector database for semantic search
- **LangChain Vector Store** - Integration layer for vector storage and retrieval

### Document Processing
- **LangChain Document Loaders** - Load documents from various sources
- **RecursiveCharacterTextSplitter** - Intelligent text chunking with overlap
- **LangChain Embeddings** - Create vector representations of text

### Development Tools
- **Python 3.10+** - Programming language
- **python-dotenv** - Environment variable management
- **pytest** - Testing framework
- **httpx** - Async HTTP client for testing

---

## 📁 Project Structure

```
healthcare-knowledge-assistant/
├── backend/                          # Core application logic
│   ├── __init__.py                   # Package initialization
│   ├── main.py                       # FastAPI application & endpoints
│   ├── config.py                     # Environment & application settings
│   ├── models.py                     # Pydantic request/response models
│   ├── document_processor.py         # Document ingestion & vector store
│   ├── rag_engine.py                 # RAG pipeline & query processing
│   ├── utils.py                      # Utility functions
│   └── tools/                        # Extensible tool system
│       ├── __init__.py
│       ├── base_tool.py              # Base class for tools
│       ├── registry.py               # Tool registration & discovery
│       ├── tool_executor.py          # Tool execution engine
│       ├── time_tools.py             # Time/date-based tools
│       └── search_tools.py           # Search tools (internal & web)
│
├── frontend/                         # React-based UI
│   └── my-medical-chatbot/
│       ├── public/
│       │   └── index.html            # Main HTML file
│       ├── src/
│       │   ├── App.js                # Main React component
│       │   ├── index.js              # Entry point
│       │   ├── index.css             # Global styles
│       │   └── components/           # Reusable UI components
│       └── package.json              # Dependencies
│
├── data/                             # Data directory
│   ├── sample_docs/                  # Knowledge base documents
│   │   ├── admission_policy.txt
│   │   ├── billing_and_insurance.txt
│   │   ├── dental_clinic_faq.txt
│   │   ├── diagnostics_pricing_guide.txt
│   │   └── visiting_hours.txt
│   ├── raw/                          # Raw data (pre-processing)
│   └── processed/                    # Processed data
│
├── vectordb/                         # Vector database storage
│   └── chroma_db/                    # ChromaDB persistent storage
│       ├── chroma.sqlite3            # SQLite metadata store
│       └── [collection_ids]/         # Vector collections
│
├── tests/                            # Test suite
│   ├── test_api.py                   # API endpoint tests
│   ├── test_ingestion.py             # Document ingestion tests
│   ├── test_rag.py                   # RAG pipeline tests
│   ├── test_rag_retrieval.py         # Retrieval quality tests
│   ├── test_tools.py                 # Tool functionality tests
│   ├── api_evaluation.py             # API performance evaluation
│   ├── rag_evaluation.py             # RAG quality metrics
│   └── results/                      # Test execution results
│
├── images/                           # Project screenshots
│   ├── 01-frontend-homepage.png
│   ├── 02-backend-base-endpoint.png
│   ├── 03-backend-endpoint-apis-list.png
│   ├── 04-backend-schemas-list.png
│   ├── 05-backend-complete-docs.png
│   ├── 06-frontend-working-demo.png
│   ├── 07-frontend-request-sent-thinking.png
│   └── 08-frontend-answer-to-question-whose-answer-is-not-there-in-documents.png
│
├── notebooks/                        # Jupyter notebooks
│   └── experiment_rag.ipynb          # RAG experimentation & analysis
│
├── requirements.txt                  # Python dependencies
├── .env.example                      # Example environment variables
├── .gitignore                        # Git ignore patterns
└── README.md                         # This file
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.10+** installed
- **pip** or **poetry** for dependency management
- **API Keys:**
  - Google Gemini API key (Primary) - Get from [AI Studio](https://aistudio.google.com/app/apikey)
  - OpenAI API key (Fallback) - Get from [OpenAI Platform](https://platform.openai.com/api-keys)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/healthcare-knowledge-assistant.git
cd healthcare-knowledge-assistant
```

### Step 2: Create Python Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example to .env
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional fallback

# Application Settings
APP_NAME="Healthcare Knowledge Assistant"
APP_VERSION="1.0.0"
DEBUG_MODE=False

# Vector Database
CHROMA_PERSIST_DIRECTORY=./vectordb/chroma_db
CHROMA_COLLECTION_NAME=healthcare_docs

# Document Processing
DOCUMENTS_PATH=./data/sample_docs
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# RAG Settings
RETRIEVAL_TOP_K=5
LLM_TEMPERATURE=0.0
LLM_MAX_OUTPUT_TOKENS=1000

# Model Selection
EMBEDDING_MODEL=models/gemini-embedding-001
CHAT_MODEL=models/gemini-2.5-flash
```

### Step 5: Prepare Knowledge Base Documents

Place your healthcare documents (as `.txt` files) in the `data/sample_docs/` directory:

```bash
# Example documents included:
ls data/sample_docs/
```

---

## ⚡ Quick Start Guide

### 1. **Ingest Documents into Vector Database**

Before querying, you must index your healthcare documents:

```bash
python -c "from backend.document_processor import document_processor; \
           document_processor.ingest_documents(force_reindex=True)"
```

**Expected Output:**
```
============================================================
Document Ingestion Pipeline Started
============================================================
📂 Loading documents from: ./data/sample_docs
✓ Loaded 5 documents
✂️ Splitting documents into chunks...
 Chunk size: 1000 tokens
 Overlap: 200 tokens
✓ Created 47 chunks from 5 documents
🗄️ Creating vector store...
 Collection: healthcare_docs
 Directory: ./vectordb/chroma_db
✓ Vector store created successfully

============================================================
✅ Ingestion Completed Successfully!
 Documents: 5
 Chunks: 47
 Time: 2.34 seconds
============================================================
```

### 2. **Start the Backend Server**

```bash
cd backend
python main.py
# or using uvicorn directly:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
✓ Using Google Gemini embeddings (models/gemini-embedding-001)...
✓ Vector database directory: ./vectordb/chroma_db
🚀 Initializing RAG Engine...
✓ LLM initialized
✓ Vector store connected
✓ Retriever configured (top_k=5)
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. **Access API Documentation**

Open your browser and navigate to:
- **Interactive Swagger UI:** http://localhost:8000/docs
- **ReDoc Documentation:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

### 4. **Start the Frontend Application**

In a new terminal:

```bash
cd frontend/my-medical-chatbot
npm install
npm start
```

The frontend will open at http://localhost:3000

### 5. **Test with Sample Queries**

Using curl or the Swagger UI, test the API:

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the visiting hours for ICU patients?",
    "user_role": "general",
    "include_sources": true
  }'
```

---

## 📡 API Endpoints Documentation

### 1. **Root Endpoint**
```
GET /
```

**Description:** API information and navigation

**Response:**
```json
{
  "message": "Welcome to Healthcare Knowledge Assistant",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### 2. **Health Check**
```
GET /health
```

**Description:** System status and vector database statistics

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "vector_db_status": "healthy",
  "document_count": 47
}
```

---

### 3. **Document Ingestion** ⭐ **MUST RUN FIRST**
```
POST /ingest
```

**Description:** Load and index documents into the vector database

**Request Body:**
```json
{
  "force_reindex": false
}
```

**Parameters:**
- `force_reindex` (boolean, default: false) - If true, clears existing collection and re-indexes

**Response:**
```json
{
  "success": true,
  "message": "Documents ingested successfully",
  "documents_processed": 5,
  "chunks_created": 47,
  "time_taken_seconds": 2.34
}
```

---

### 4. **Query Knowledge Base** ⭐ **MAIN ENDPOINT**
```
POST /query
```

**Description:** Submit questions to the healthcare knowledge base using RAG

**Request Body:**
```json
{
  "question": "What are the visiting hours for ICU patients?",
  "user_role": "general",
  "include_sources": true
}
```

**Request Parameters:**
- `question` (string, required) - The healthcare question (3-500 characters)
- `user_role` (enum, default: "general") - One of: "doctor", "receptionist", "billing", "general"
- `include_sources` (boolean, default: true) - Include source documents in response

**Response:**
```json
{
  "question": "What are the visiting hours for ICU patients?",
  "answer": "Based on our records, ICU visiting hours are:\n- Regular Hours: 9 AM to 5 PM\n- Emergency Visits: 24/7 with prior authorization\n- Maximum visitors per patient: 2 at a time",
  "sources": [
    {
      "filename": "visiting_hours.txt",
      "chunk_index": 2,
      "relevance_score": 0.95,
      "content_preview": "Intensive Care Unit (ICU) Visiting Hours:\nRegular visiting hours are from 9:00 AM to 5:00 PM daily..."
    }
  ],
  "user_role": "general",
  "disclaimer": "⚠️ IMPORTANT DISCLAIMER: This information is for general guidance only. For medical advice, diagnosis, or treatment, please consult with qualified healthcare professionals. In case of emergency, call 911 or visit the Emergency Department immediately.",
  "processing_time_seconds": 1.45,
  "tools_used": []
}
```

---

### 5. **Get Statistics**
```
GET /stats
```

**Description:** Application configuration and statistics

**Response:**
```json
{
  "total_chunks": 47,
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "embedding_model": "models/gemini-embedding-001",
  "chat_model": "models/gemini-2.5-flash",
  "retrieval_top_k": 5,
  "collection_name": "healthcare_docs",
  "provider": "Gemini (Google AI)"
}
```

---

### 6. **List Available Tools**
```
GET /tools
```

**Description:** Retrieve all available MCP tools and their schemas

**Response:**
```json
{
  "status": "success",
  "total_tools": 5,
  "tools": [
    "get_current_datetime",
    "calculate_age",
    "get_working_hours",
    "search_internal_docs",
    "web_search"
  ],
  "schemas": [
    {
      "type": "function",
      "function": {
        "name": "get_current_datetime",
        "description": "Get current date, time, day of week, and timestamp",
        "parameters": {
          "type": "object",
          "properties": {
            "timezone": {
              "type": "string",
              "description": "IANA timezone (e.g., 'Asia/Kolkata', 'UTC')"
            }
          }
        }
      }
    }
  ]
}
```

---

### 7. **Execute Tool Manually**
```
POST /execute-tool
```

**Description:** Execute a specific tool with custom parameters (useful for debugging)

**Query Parameters:**
- `tool_name` (string, required) - Name of the tool to execute
- `params` (object, optional) - Tool parameters

**Request Body:**
```json
{
  "timezone": "Asia/Kolkata"
}
```

**Response:**
```json
{
  "status": "success",
  "tool": "get_current_datetime",
  "result": {
    "current_date": "2025-11-18",
    "current_time": "12:30:45",
    "day_of_week": "Tuesday",
    "timestamp": 1700297445,
    "timezone": "Asia/Kolkata"
  }
}
```

---

## 🧠 How the Bot Works: RAG Architecture Explained

### **Phase 1: Document Ingestion**

```
Raw Documents
      ↓
Load from Disk (DocumentProcessor)
      ↓
Chunk Text (RecursiveCharacterTextSplitter)
  - Chunk size: 1000 tokens
  - Overlap: 200 tokens (for context)
      ↓
Generate Embeddings (Gemini/OpenAI)
  - Convert text → vector representation
  - Dimensions: 768 (balanced)
      ↓
Store in Vector DB (ChromaDB)
  - Persistent storage: ./vectordb/chroma_db
  - Fast similarity search ready
```

### **Phase 2: Query Processing**

```
User Question
      ↓
1. RETRIEVAL (Semantic Search)
   └─ Convert question → embedding
   └─ Search vector DB (cosine similarity)
   └─ Retrieve top-K relevant chunks (k=5)
      ↓
2. AUGMENTATION (Context Building)
   └─ Combine retrieved chunks with question
   └─ Apply role-specific system prompt
   └─ Format as LLM input
      ↓
3. GENERATION (LLM Response)
   └─ Send to LLM (Gemini/OpenAI)
   └─ Generate response based on context
   └─ Apply safety filters
      ↓
4. POST-PROCESSING
   └─ Extract sources from retrieved chunks
   └─ Calculate relevance scores
   └─ Add medical disclaimer
      ↓
Response JSON
```

### **Key Advantages of RAG**

| Feature | Benefit |
|---------|---------|
| **Grounded Responses** | Answers strictly based on indexed documents; no hallucinations |
| **Explainability** | Source documents provided for verification |
| **Up-to-date Info** | Easy to update knowledge base by adding documents |
| **Cost-Efficient** | Reduces API calls with smaller context windows |
| **Fact-Checked** | Information must exist in knowledge base |

---

## 🔒 Safety & Relevance Mechanisms

### How This Bot Does NOT Answer Irrelevant Questions

#### **1. Context-Only Constraint**
The system uses explicit prompting to enforce context adherence:

```python
# From rag_engine.py - Role-Specific Prompts
"SAFETY RULES (CRITICAL):
1. ONLY use information from provided context
2. If information is not in context, state 'I don't have that information in our records'
3. Do NOT make up information not in the context"
```

**Example:**
```
Q: "What's the weather today?"
A: "I don't have that information in our records. I'm specifically designed 
   to answer questions about hospital policies and procedures. Is there 
   anything related to our hospital services I can help with?"
```

#### **2. Vector Search Filtering**
Only documents with sufficient semantic similarity are retrieved:

```python
# From config.py
RETRIEVAL_TOP_K = 5  # Get top-5 most relevant chunks
LLM_TEMPERATURE = 0.0  # Deterministic (no creativity)
```

**Process:**
- User question converted to embedding
- Cosine similarity calculated to all document embeddings
- Only top-5 most similar chunks retrieved
- LLM forced to use ONLY these chunks

#### **3. Medical Safety Guards**

All role-specific prompts include critical safety rules:

```python
DOCTOR_PROMPT = """
SAFETY RULES (CRITICAL):
1. NEVER provide medical diagnosis
2. NEVER prescribe medications or recommend dosages
3. NEVER provide treatment recommendations
4. ONLY use information from provided context
5. For emergencies, direct to call 911
"""
```

#### **4. Explicit Out-of-Scope Detection**

The system explicitly states what it cannot do:

**Cannot Answer:**
- ❌ Medical diagnosis ("You have diabetes")
- ❌ Medication prescriptions ("Take 500mg Amoxicillin")
- ❌ Treatment plans ("Do 10 sessions of physiotherapy")
- ❌ Unrelated topics ("What's the capital of France?")
- ❌ Personal medical advice ("Based on your symptoms...")

**Can Answer:**
- ✅ Hospital policies and procedures
- ✅ Visiting hours and admission process
- ✅ Billing and insurance information
- ✅ Facility locations and departments
- ✅ General health information (with disclaimer)

#### **5. Medical Disclaimer on Every Response**

```
⚠️ IMPORTANT DISCLAIMER:
This information is for general guidance only. For medical advice, diagnosis, 
or treatment, please consult with qualified healthcare professionals. 
In case of emergency, call 911 or visit the Emergency Department immediately.
```

#### **6. Example: Out-of-Scope Question**

```json
// INPUT
{
  "question": "I have chest pain, what medication should I take?",
  "user_role": "general"
}

// OUTPUT
{
  "answer": "⚠️ I cannot provide medical advice or medication recommendations. 
             If you're experiencing chest pain, this could be a serious medical 
             emergency. Please call 911 immediately or visit the nearest 
             Emergency Department right away. 
             
             If you have questions about our emergency services or 
             how to reach our ER, I'd be happy to help with that information.",
  "disclaimer": "⚠️ IMPORTANT DISCLAIMER: This information is for general 
                 guidance only. For medical advice, diagnosis, or treatment, 
                 please consult with qualified healthcare professionals..."
}
```

#### **7. No Hallucination Example**

```json
// INPUT - Question not in knowledge base
{
  "question": "What's your hospital's policy on pet visitation?",
  "user_role": "general"
}

// OUTPUT - Honest "I don't know" instead of making something up
{
  "answer": "I don't have information about pet visitation policies in our 
             current knowledge base. For this specific question, please 
             contact our front desk at [contact info] or speak with 
             our admission staff. They'll be able to provide you with 
             accurate information about our pet policy.",
  "sources": [],  // No sources retrieved (question not relevant to docs)
  "tools_used": []
}
```

---

## ⚙️ Configuration

All settings are managed through environment variables in `.env` file:

### **LLM & API Configuration**

```env
# Primary LLM Provider (Gemini)
GEMINI_API_KEY=your_gemini_api_key

# Fallback LLM Provider (Optional)
OPENAI_API_KEY=your_openai_api_key
```

### **Application Settings**

```env
APP_NAME=Healthcare Knowledge Assistant
APP_VERSION=1.0.0
DEBUG_MODE=False  # Set to True for development
```

### **Vector Database**

```env
CHROMA_PERSIST_DIRECTORY=./vectordb/chroma_db
CHROMA_COLLECTION_NAME=healthcare_docs
```

### **Document Processing**

```env
DOCUMENTS_PATH=./data/sample_docs
CHUNK_SIZE=1000         # Characters per chunk
CHUNK_OVERLAP=200       # Overlap between chunks
```

### **RAG Parameters**

```env
RETRIEVAL_TOP_K=5              # Number of chunks to retrieve
LLM_TEMPERATURE=0.0            # 0=deterministic, 1=creative
LLM_MAX_OUTPUT_TOKENS=1000     # Max response length
```

### **Model Selection**

```env
# Embedding model (creates vectors from text)
EMBEDDING_MODEL=models/gemini-embedding-001

# Chat model (generates responses)
CHAT_MODEL=models/gemini-2.5-flash
```

### **Switching LLM Providers**

To use OpenAI instead of Gemini:

```env
# Comment out Gemini
# GEMINI_API_KEY=xxx

# Enable OpenAI
OPENAI_API_KEY=sk-xxx
CHAT_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-large
```

---

## 🚀 Deployment

### **Local Development**

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend/my-medical-chatbot
npm start
```

### **Docker Deployment**

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-c", "from backend.document_processor import document_processor; \
    document_processor.ingest_documents(force_reindex=True)"] && \
    ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Deploy to Render (Recommended for Students)**

1. Push code to GitHub
2. Connect GitHub repo to Render
3. Set environment variables in Render dashboard
4. Deploy! Your API will be available at `https://your-app.onrender.com`

### **Deploy to AWS/GCP/Azure**

All these platforms support FastAPI applications. Refer to their documentation for Python app deployment.

---

## 🧪 Testing & Evaluation

### **Run All Tests**

```bash
pytest tests/ -v
```

### **Test Document Ingestion**

```bash
python tests/test_ingestion.py
```

**Expected Output:**
```
✓ Successfully loaded 5 documents
✓ Created 47 chunks
✓ Vector store initialized
✓ Similarity search working
```

### **Test RAG Pipeline**

```bash
python tests/test_rag.py
```

### **Evaluate API Endpoints**

```bash
python tests/api_evaluation.py
```

### **RAG Quality Metrics**

```bash
python tests/rag_evaluation.py
```

Generates evaluation report with:
- Answer relevance score
- Context utilization
- Response latency
- Source attribution quality

---

## 🔮 Future Enhancements

- [ ] **Document Upload UI:** Upload documents via frontend
- [ ] **Query History:** Store and retrieve previous questions
- [ ] **Analytics Dashboard:** Query trends and popular questions
- [ ] **Fine-tuned Models:** Custom LLM fine-tuned on hospital data
- [ ] **Conversation Memory:** Context from previous messages
- [ ] **Voice Interface:** Speak questions, hear responses
- [ ] **Database Integration:** Connect to actual hospital databases
- [ ] **Compliance Features:** HIPAA compliance, data encryption

---

## 📚 Sample Knowledge Base Documents

The project includes sample healthcare documents:

1. **admission_policy.txt** - Hospital admission procedures and requirements
2. **billing_and_insurance.txt** - Billing policies, insurance processing
3. **dental_clinic_faq.txt** - Dental services FAQ
4. **diagnostics_pricing_guide.txt** - Diagnostic tests and pricing
5. **visiting_hours.txt** - Visiting hours for different departments

**To add your own documents:**
1. Create `.txt` files in `data/sample_docs/`
2. Run ingestion: `python -c "from backend.document_processor import document_processor; document_processor.ingest_documents(force_reindex=True)"`
3. Query will use new documents immediately

---

## 🏆 Project Highlights for Job Applications

This project demonstrates **Advanced AI/ML** (RAG, LangChain, vector databases, multi-LLM integration), **Backend Development** (FastAPI, async Python, RESTful APIs), **DevOps** (Docker, cloud deployment, CI/CD), **Software Engineering Best Practices** (modular architecture, testing, documentation), and **Real-World Problem Solving** (healthcare domain, safety-critical systems, role-based access control).

---


## 📖 Documentation & Resources

- **LangChain Docs:** https://python.langchain.com/
- **ChromaDB Guide:** https://docs.trychroma.com/
- **FastAPI Tutorial:** https://fastapi.tiangolo.com/
- **Gemini API Docs:** https://ai.google.dev/docs
- **RAG Overview:** https://docs.langchain.com/use_cases/qa_over_docs

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is open source and available under the MIT License.

---

## 📞 Support & Contact

**Author:** Abhishek Suwalka  
**Email:** suwalkabhishek@gmail.com  
**LinkedIn:** [AbhishekSuwalka](http://linkedin.com/in/AbhishekSuwalka)  
**GitHub:** [Abhisheksuwalka](https://github.com/Abhisheksuwalka)

**For Issues & Questions:**
- Open an issue on GitHub
- Email: suwalkabhishek@gmail.com
- Check existing documentation first

---

## 🙏 Acknowledgments

- **LangChain** for the amazing RAG framework
- **Google Gemini API** for state-of-the-art LLM (and also for free tier plan)
- **Chroma** for fast vector search
- **FastAPI** for modern Python web framework
- **OpenAI** for fallback LLM support

---

**Last Updated:** November 18, 2025  
**Status:** Production Ready ✅  
**Version:** 1.0.0

---

## ⭐ Quick Reference: Common Commands

```bash
# Environment setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Document ingestion (MUST RUN FIRST)
python -c "from backend.document_processor import document_processor; \
           document_processor.ingest_documents(force_reindex=True)"

# Start backend
cd backend && python main.py

# Start frontend (new terminal)
cd frontend/my-medical-chatbot && npm start

# Run tests
pytest tests/ -v

# Access API docs
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)

# Test with curl
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question":"What are visiting hours?","user_role":"general"}'
```

---


## 📸 Project Screenshots

### Frontend Interface
![Frontend Homepage](./images/01-frontend-homepage.png)
*Healthcare Knowledge Assistant - User Interface*

![Working Demo](./images/06-frontend-working-demo.png)
*Live chat interaction with the AI assistant*

![Request Processing](./images/07-frontend-request-sent-thinking.png)
*Real-time query processing indicator*

![Out-of-Scope Response](./images/08-frontend-answer-to-question-whose-answer-is-not-there-in-documents.png)
*Intelligent handling of questions not in knowledge base*

### Backend API Documentation
![Base Endpoint](./images/02-backend-base-endpoint.png)
*FastAPI root endpoint with API information*

![API Endpoints List](./images/03-backend-endpoint-apis-list.png)
*Complete list of available REST API endpoints*

![API Schemas](./images/04-backend-schemas-list.png)
*Request/response schemas and data models*

![Complete Documentation](./images/05-backend-complete-docs.png)
*Interactive Swagger UI documentation*

---



**Enjoy building with Healthcare Knowledge Assistant! 🚀**
