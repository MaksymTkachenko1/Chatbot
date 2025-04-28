# LLM Basics Module Implementation

## TLDR
This project implements three key components:
1. Team Composition Generator using Pydantic and LLM
2. Question-Answering RAG System with Chroma DB
3. Chatbot with Wikipedia Integration and Math Retrieval

## Prerequisites
- Python 3.12+
- OpenAI API key
- ~2GB disk space for dataset and vector store

## Quick Start (Windows)

### 1. Poetry Setup
```powershell
# Install pipx if you haven't already
python -m pip install --user pipx
python -m pipx ensurepath

# Install Poetry using pipx
pipx install poetry

# Verify installation
poetry --version
```

### 2. Project Setup
```powershell
# Clone the repository
git clone [repo-url]
cd nlp-course

# Install dependencies using Poetry
poetry install --with llm --no-root 
```

### 3. Data Setup

Manual Setup
1. Download dataset from: [dataset_doc.zip] (private dataset)
2. Create directory structure:
```
nlp-course/
├── dataset_doc/
│   ├── train/
│   │   ├── 1401.0001/
│   │   ├── 1401.0223/
│   │   ├── 1401.0336/
│   │   ├── 1401.0349/
│   │   └── 1401.0616/
│   └── test/
│       ├── 1401.0001/
│       ├── 1401.0223/
│       ├── 1401.0336/
│       ├── 1401.0349/
│       └── 1401.0616/
```

### 4. Environment Setup
```powershell
# Create .env file
Copy-Item .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_key_here
```

### 5. Launch Jupyter Lab
```powershell
# Using Poetry
poetry run jupyter lab

# Or after activating environment
jupyter lab
```

## Project Structure
```
nlp-course/
├── Module_2_LLM_basics/
│   ├── src/
│   │   ├── loader.py      # Document loader implementation
│   │   ├── retriever.py   # Custom retriever for Chroma DB
│   │   └── parser.py      # Article parsing utilities
│   ├── docs/
│   │   └── chroma_db/     # Will be created automatically
│   └── notebooks/
│       ├── 01_llm_basics.ipynb
│       ├── 02_rag_basics.ipynb
│       └── 03_rag_chatbot.ipynb
├── dataset_doc/           # Data directory
├── data_loader.py  
├── pyproject.toml         # Poetry dependencies
└── .env                   # Environment variables
```

## Implementation Details

### RAG System Components:
1. **Document Loader** (`ArticleLoader`)
   - Implements lazy loading for JSON files
   - Uses `process_article` for text and metadata extraction
   - Returns `langchain_core.documents.Document` instances

2. **Custom Retriever** (`ArticleRetriever`)
   - Supports filtering via `query_filter`
   - Uses Chroma DB for similarity search
   - Returns top-k relevant documents

3. **QA Chain**
   - Uses OpenAI embeddings and GPT-4
   - Supports document-specific queries
   - Returns "That's beyond the scope of my knowledge" for out-of-scope queries

## Data Management
- Large files (dataset, vector stores) are excluded from git
- Use `data_loader.py` for dataset setup
- Chroma DB files are regenerated locally

## Troubleshoting

Try restart kernel and run all code cells in Jupyter Lab.