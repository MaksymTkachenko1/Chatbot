# Notebook Fixes and Improvements

## Problems Fixed

### 1. Import and Path Issues
**Problem**: Unsafe `sys.path` modification and relative imports
**Solution**: Use the new `notebook_setup.py` module for safe imports

### 2. Hardcoded Values
**Problem**: Hardcoded paths and configuration values
**Solution**: Use centralized configuration from `configs/config.py`

## How to Update Your Notebooks

### Option 1: Use the Setup Module (Recommended)

Replace the problematic import cell with:

```python
# Safe imports and setup
from Module_2_LLM_basics.src.notebook_setup import quick_setup

# Get all necessary imports and configurations
notebook_vars = quick_setup()

# Extract variables for use
config = notebook_vars['config']
ArticleLoader = notebook_vars['ArticleLoader']
ArticleRetriever = notebook_vars['ArticleRetriever']
Chroma = notebook_vars['Chroma']
llm = notebook_vars['llm']
embeddings_model = notebook_vars['embeddings_model']
persist_directory = notebook_vars['persist_directory']
json_dir = notebook_vars['json_dir']
# ... and so on for other variables you need
```

### Option 2: Manual Fix

Replace the original import cell with:

```python
import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path more safely
project_root = Path(__file__).parent.parent if '__file__' in globals() else Path().resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Import configuration and setup logging
try:
    from Module_2_LLM_basics.configs.config import get_config
    config = get_config()
    config.setup_logging()
except ImportError:
    # Fallback if config module is not available
    logging.basicConfig(level=logging.INFO)
    config = None

from Module_2_LLM_basics.src.loader import ArticleLoader
from Module_2_LLM_basics.src.retriever import ArticleRetriever

from langchain_chroma import Chroma
import glob
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool, render_text_description_and_args
from langchain_core.messages import SystemMessage
from uuid import uuid4
from IPython.display import display, Markdown

# Initialize models with configuration
llm = ChatOpenAI(model='gpt-4o-mini')

if config:
    embeddings_model = OpenAIEmbeddings(model=config.retriever.default_embedding_model)
    persist_directory = config.vectordb.persist_directory
    JSON_DIR = config.data.json_data_dir
    
    # Validate configuration
    if not config.validate():
        logging.warning("Configuration validation failed, proceeding with default values")
else:
    # Fallback values
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
    persist_directory = 'docs/chroma/'
    JSON_DIR = "../dataset_doc/train"

print(f"OpenAI API Key Loaded: {'OPENAI_API_KEY' in os.environ and bool(os.environ.get('OPENAI_API_KEY'))}")
print(f"LLM Model Name: {llm.model_name}")
print(f"Embeddings Model Name: {embeddings_model.model}")
print(f"Using persist directory: {persist_directory}")
print(f"Using JSON data directory: {JSON_DIR}")
```

## Environment Variables

You can now configure the application using environment variables:

```bash
export LOG_LEVEL=DEBUG
export LOG_FILE=logs/app.log
export MIN_PARAGRAPH_LENGTH=30
export DEFAULT_K=10
export CHROMA_PERSIST_DIR=custom/chroma/path
export JSON_DATA_DIR=custom/json/path
export MAX_ARTICLES=100
```

## Configuration Benefits

1. **Centralized Settings**: All configuration in one place
2. **Environment-based**: Easy to change settings without code changes
3. **Validation**: Automatic validation of configuration values
4. **Logging**: Proper logging setup with configurable levels
5. **Error Handling**: Robust error handling throughout the codebase
6. **Type Safety**: Proper type annotations and validation

## Code Quality Improvements

1. **Error Handling**: All file operations now have proper exception handling
2. **Logging**: Comprehensive logging throughout the application
3. **Type Annotations**: Complete type hints for better IDE support and code clarity
4. **Validation**: Input validation in all public methods
5. **Documentation**: Detailed docstrings with examples and error descriptions
6. **Configuration**: Centralized, environment-aware configuration system