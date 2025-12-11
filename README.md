# Medical Report Tracker

A comprehensive web application for tracking and querying patient lab results over time using Retrieval-Augmented Generation (RAG) technology. This application processes multiple lab reports, builds a vector database for efficient searching, and provides an AI-powered interface to answer questions about patient health data.

## 📋 Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [How It Works](#how-it-works)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [How to Run](#how-to-run)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)

## 🎯 Introduction

The **Medical Report Tracker** is designed to analyze patient lab results across multiple time periods. The system:

- **Tracks Lab Results**: Manages multiple lab reports for patients over extended periods
- **Builds RAG Pipeline**: Automatically chunks and embeds lab report data into a vector database for efficient retrieval
- **Answers Questions**: Uses AI to answer natural language questions about patient lab results, trends, and health metrics

For testing and demonstration purposes, the project uses the **Faker** library to generate realistic patient data and the **ReportLab** library to create standardized PDF lab reports that mimic real-world medical documents.

## ✨ Features

- **Patient Management**: View and select from a list of patients with their lab reports
- **Sample Data Generation**: Generate realistic lab reports for testing with customizable parameters
- **RAG Pipeline Processing**: Automatically process all lab reports, chunk them, and create embeddings
- **AI-Powered Q&A**: Ask natural language questions about patient lab results
- **Patient-Specific Context**: Automatically filter queries by selected patient
- **Web-Based UI**: Modern, responsive interface for easy interaction
- **Multiple LLM Support**: Works with OpenAI, Groq, and Google Gemini APIs

## 🔧 How It Works

The application uses a **Retrieval-Augmented Generation (RAG)** pipeline to answer questions about patient lab reports:

1. **Document Loading**: PDF lab reports are loaded from the `data/` directory
2. **Text Extraction**: Text content is extracted from PDF files using PyPDF
3. **Chunking**: Documents are split into smaller, manageable chunks using LangChain's RecursiveCharacterTextSplitter
4. **Embedding**: Each chunk is converted into a vector embedding using HuggingFace's sentence-transformers model
5. **Vector Storage**: Embeddings are stored in ChromaDB, a persistent vector database
6. **Query Processing**: When a question is asked:
   - The query is converted to an embedding
   - Similar chunks are retrieved from the vector database
   - If a patient is selected, results are filtered to that patient
   - Retrieved context is combined with the question
   - An LLM generates a response based on the retrieved context

## 🛠 Technology Stack

- **Backend Framework**: FastAPI
- **Vector Database**: ChromaDB
- **Embeddings**: HuggingFace Sentence Transformers (`all-MiniLM-L6-v2`)
- **LLM Integration**: LangChain (supports OpenAI, Groq, Google Gemini)
- **PDF Processing**: PyPDF
- **Report Generation**: ReportLab, Faker
- **Frontend**: HTML, CSS, JavaScript
- **Text Processing**: LangChain Text Splitters

## 📁 Project Structure

```
medical-report-tracker/
├── src/
│   ├── app.py                 # FastAPI application with API endpoints
│   ├── rag_assistant.py       # RAG assistant implementation
│   ├── vectordb.py            # Vector database wrapper (ChromaDB)
│   ├── llms.py                # LLM initialization and configuration
│   ├── labreport_generator.py # Lab report PDF generator
│   ├── templates/
│   │   └── index.html         # Web UI template
│   └── utils/
│       └── prompt_builder.py  # Prompt template builder
├── data/                      # Directory for lab report PDFs
├── chroma_db/                 # ChromaDB persistent storage
├── config/
│   └── prompts.yaml           # RAG prompt templates
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 📋 Prerequisites

Before running the application, ensure you have:

- **Python 3.8 or higher**
- **API Key** from one of the following providers:
  - [OpenAI](https://platform.openai.com/api-keys) (recommended)
  - [Groq](https://console.groq.com/keys) (free tier available)
  - [Google AI](https://aistudio.google.com/app/apikey)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sajadreshi/medical-report-tracker.git
cd medical-report-tracker
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root and add your API key:

```bash
# Choose one of the following:
OPENAI_API_KEY=your_openai_api_key_here
# OR
GROQ_API_KEY=your_groq_api_key_here
# OR
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Specify model preferences
OPENAI_MODEL=gpt-4o-mini
GROQ_MODEL=llama-3.1-8b-instant
GOOGLE_MODEL=gemini-1.5-flash

# Optional: RAG configuration
RAG_N_RESULTS=50
CHROMA_COLLECTION_NAME=rag_lab_reports
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 🎮 How to Run

### Step 1: Start the Application

Run the FastAPI server:

```bash
python src/app.py
```

Alternatively, you can use uvicorn directly:

```bash
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Access the Web Interface

Open your web browser and navigate to:

```
http://localhost:8000/medicalreport/
```

You should see the Medical Report Tracker interface with three main buttons at the top.

### Step 3: Generate Sample Data

1. Click the **"Generate Sample Data"** button (green button with beaker icon)
2. This will create sample lab reports in the `data/` directory
3. By default, it generates 3 patients with 4 reports each (12 total reports)
4. Reports are saved as PDF files with the naming pattern: `LabReport_{PatientName}_Report{Number}_{Date}.pdf`

### Step 4: Process RAG Pipeline

1. Click the **"Process RAG Pipeline"** button (blue-to-pink gradient button with rocket icon)
2. Wait for the processing to complete (this may take a few moments)
3. You should see a success message indicating how many documents were processed
4. The system will:
   - Load all PDF files from the `data/` directory
   - Extract text content
   - Chunk the documents
   - Create embeddings
   - Store everything in the vector database

### Step 5: List Patients

1. Click the **"List Patients"** button (purple button with document icon)
2. You'll see a list of unique patient names extracted from the lab reports
3. Click on any patient name to select them (the name will be highlighted)

### Step 6: Ask Questions

1. With a patient selected, the chat interface at the bottom will update to show the patient's name
2. Type your question in the input field (e.g., "How has the cholesterol level improved over the last few months?")
3. Click **"Send"** or press Enter
4. The AI will search through the patient's lab reports and provide an answer based on the retrieved context

## 💡 Usage Examples

Here are some example questions you can ask about patients:

### General Questions
- "Show me how has the patient's cholesterol levels improved over the last 3 months"
- "Give me a summary of glucose levels about the patient"
- "What are the patient's latest lab results?"
- "Compare the patient's HDL and LDL cholesterol levels across all reports"

### Specific Metrics
- "What is the patient's current hemoglobin level?"
- "Show me the trend in triglyceride levels"
- "What are the patient's liver function test results?"
- "Has the patient's A1C level changed over time?"

### Trend Analysis
- "How have the patient's lab values changed over the past 4 months?"
- "Are there any abnormal values in the patient's recent reports?"
- "What improvements or concerns are there in the patient's health metrics?"

### Patient-Specific Queries
When a patient is selected, all questions are automatically scoped to that patient.

## ⚙️ Configuration

### Environment Variables

The application supports the following environment variables (in `.env` file):

#### API Keys (Required - choose one)
- `OPENAI_API_KEY`: Your OpenAI API key
- `GROQ_API_KEY`: Your Groq API key
- `GOOGLE_API_KEY`: Your Google AI API key

#### Model Selection (Optional)
- `OPENAI_MODEL`: Model name for OpenAI (default: `gpt-4o-mini`)
- `GROQ_MODEL`: Model name for Groq (default: `llama-3.1-8b-instant`)
- `GOOGLE_MODEL`: Model name for Google (default: `gemini-1.5-flash`)

#### RAG Configuration (Optional)
- `RAG_N_RESULTS`: Number of document chunks to retrieve (default: `50`)
- `CHROMA_COLLECTION_NAME`: Name of the ChromaDB collection (default: `rag_lab_reports`)
- `EMBEDDING_MODEL`: HuggingFace embedding model (default: `sentence-transformers/all-MiniLM-L6-v2`)

### Customizing Sample Data Generation

You can modify the sample data generation by editing `src/labreport_generator.py`:

```python
# In src/app.py, the generate_data endpoint calls:
generate_lab_reports(
    num_patients=3,        # Number of patients
    reports_per_patient=4, # Reports per patient
    date_interval_months=1 # Months between reports
)
```

## 🔍 How the RAG Pipeline Works

1. **Document Processing**:
   - PDFs are loaded and text is extracted
   - Metadata (patient name, report number, date) is extracted from filenames
   - Documents are chunked into ~500 character segments with 10% overlap

2. **Embedding Creation**:
   - Each chunk is converted to a vector using sentence transformers
   - Embeddings capture semantic meaning for better search

3. **Vector Storage**:
   - Embeddings are stored in ChromaDB with associated metadata
   - Metadata includes patient name, report number, and date for filtering

4. **Query Processing**:
   - User question is converted to an embedding
   - Similar chunks are retrieved from the vector database
   - If a patient is selected, results are filtered to that patient
   - Retrieved context is formatted and sent to the LLM

5. **Response Generation**:
   - LLM receives the question and retrieved context
   - LLM generates a response based on the context
   - Response is formatted and displayed in the UI

## 🐛 Troubleshooting

### No API Key Error
If you see an error about missing API keys, ensure your `.env` file is in the project root and contains at least one API key.

### No Documents Found
If the RAG pipeline reports no documents found:
1. Make sure you've clicked "Generate Sample Data" first
2. Check that PDF files exist in the `data/` directory
3. Verify file naming follows the pattern: `LabReport_{PatientName}_Report{Number}_{Date}.pdf`

### Vector Database Issues
If you encounter issues with the vector database:
- The `chroma_db/` directory stores the vector database
- You can delete this directory to start fresh (it will be recreated)
- Ensure you have write permissions in the project directory



---

**Note**: This application is designed for demonstration and testing purposes. The generated lab reports use fake data and should not be used for actual medical purposes.
