# 🏥 Medical Report Tracker

A RAG-powered patient lab report analysis system that allows healthcare administrators to track patient lab results over time and ask natural language questions about patient health trends.

## ✨ Features

- **🔐 Admin Authentication** - Secure login/registration for administrators
- **👥 Patient Management** - Register, search, and manage patients
- **📄 Lab Report Generation** - Generate realistic synthetic lab reports for testing
- **🚀 RAG Pipeline** - Process documents into a searchable vector database
- **💬 AI Chat Assistant** - Ask natural language questions about patient lab results
- **📊 Trend Analysis** - Track changes in patient health metrics over time

## 🖼️ Screenshots

### Home Page
The landing page with navigation to the admin dashboard.

### Admin Dashboard
- Patient list with search functionality
- Generate lab reports for selected patients
- Process RAG pipeline for patient documents
- AI chat assistant for querying patient data

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Frontend | HTML, CSS, JavaScript |
| Vector Database | ChromaDB |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| LLM | OpenAI / Groq / Google AI |
| Application Database | SQLite |
| PDF Generation | ReportLab |
| Authentication | JWT (JSON Web Tokens) |

## 📁 Project Structure

```
medical-report-tracker/
├── src/
│   ├── app.py              # FastAPI application & routes
│   ├── database.py         # SQLite database setup
│   ├── models.py           # Pydantic models
│   ├── auth.py             # JWT authentication
│   ├── vectordb.py         # ChromaDB vector database
│   ├── rag_assistant.py    # RAG pipeline logic
│   ├── llms.py             # LLM provider configuration
│   ├── labreport_generator.py  # Synthetic lab report generator
│   └── templates/
│       ├── home.html       # Landing page
│       ├── index.html      # Admin dashboard
│       └── login.html      # Login/Register page
├── data/                   # Generated PDF lab reports
├── chroma_db/              # Vector database storage (auto-created)
├── config/
│   └── prompts.yaml        # LLM prompt templates
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- An API key from one of these LLM providers:
  - [OpenAI](https://platform.openai.com/api-keys)
  - [Groq](https://console.groq.com/keys) (free tier available)
  - [Google AI](https://aistudio.google.com/app/apikey)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sajadreshi/medical-report-tracker.git
   cd medical-report-tracker
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API key:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API key:
   ```
   OPENAI_API_KEY=your_key_here
   # OR
   GROQ_API_KEY=your_key_here
   # OR
   GOOGLE_API_KEY=your_key_here
   ```

5. **Run the application:**
   ```bash
   python src/app.py
   ```

6. **Open in browser:**
   ```
   http://localhost:8000/medicalreport/
   ```

## 📖 How to Use

### 1. Register an Admin Account
- Navigate to `http://localhost:8000/medicalreport/`
- Click on **Admin Dashboard** or **Sign In**
- Click **Register** tab and create an account
- Sign in with your credentials

### 2. Register a Patient
- Click **➕ Register New Patient**
- Fill in patient details (name, date of birth, sex)
- Click **Register Patient**

### 3. Generate Lab Reports
- Select a patient from the list
- Click **Generate Reports** button
- Choose number of reports and interval
- Click **Generate Reports**

### 4. Process RAG Pipeline
- With a patient selected, click **Process Pipeline**
- Wait for the documents to be chunked, embedded, and stored
- You'll see a success message when complete

### 5. Ask Questions
- Switch to the **Chat Assistant** tab
- With a patient selected, type questions like:
  - "What is the patient's current hemoglobin level?"
  - "Show me the trend in cholesterol levels"
  - "Are there any abnormal liver function results?"
  - "How has the patient's glucose changed over time?"

### 6. Delete a Patient
- Click the 🗑️ icon next to any patient
- Confirm the deletion
- This removes the patient, their PDF files, and vector database entries

## 💡 Example Questions

Once you've processed the RAG pipeline for a patient, try asking:

| Question | What it shows |
|----------|---------------|
| "What is the patient's current hemoglobin level?" | Latest hemoglobin value |
| "Show me the trend in triglyceride levels" | Values across all reports with trend analysis |
| "What are the patient's liver function test results?" | AST, ALT, and protein levels |
| "Are there any values outside the reference range?" | Flags abnormal results |
| "Give me a summary of the patient's metabolic panel" | Overview of glucose, electrolytes, etc. |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `GROQ_API_KEY` | Groq API key | - |
| `GOOGLE_API_KEY` | Google AI API key | - |
| `CHROMA_COLLECTION_NAME` | Vector DB collection name | `rag_lab_reports` |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |

### Database Files

| File | Purpose | Auto-created |
|------|---------|--------------|
| `medical_reports.db` | Admin users, patients, lab reports | ✅ Yes |
| `chroma_db/` | Vector embeddings for RAG | ✅ Yes |

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   FastAPI        │────▶│   SQLite DB     │
│   (HTML/JS)     │     │   Backend        │     │   (Users/Patients)
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   RAG Pipeline   │
                    └──────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌─────────────────┐ ┌────────────┐ ┌─────────────────┐
    │  PDF Documents  │ │  ChromaDB  │ │   LLM Provider  │
    │  (Lab Reports)  │ │ (Vectors)  │ │ (OpenAI/Groq)   │
    └─────────────────┘ └────────────┘ └─────────────────┘
```

## 📝 API Endpoints

### Authentication
- `POST /medicalreport/api/auth/register` - Register new admin
- `POST /medicalreport/api/auth/login` - Login and get JWT token
- `GET /medicalreport/api/auth/me` - Get current admin info

### Patient Management
- `POST /medicalreport/api/admin/patients` - Create patient
- `GET /medicalreport/api/admin/patients` - List all patients
- `GET /medicalreport/api/admin/patients/search` - Search patients
- `DELETE /medicalreport/api/admin/patients/{id}` - Delete patient

### Lab Reports & RAG
- `POST /medicalreport/api/admin/patients/{id}/generate-reports` - Generate reports
- `POST /medicalreport/api/admin/patients/{id}/process-rag` - Process RAG pipeline
- `POST /medicalreport/api/chat` - Chat with AI assistant

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built as part of the AAIDC (Applied AI Development Course) curriculum
- Uses [ChromaDB](https://www.trychroma.com/) for vector storage
- Uses [Sentence Transformers](https://www.sbert.net/) for embeddings
- Uses [LangChain](https://www.langchain.com/) for LLM orchestration
