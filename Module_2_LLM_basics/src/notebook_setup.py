"""
Setup module for notebooks.

This module provides proper imports and configuration setup for Jupyter notebooks.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

def setup_notebook_environment():
    """
    Set up the notebook environment with proper imports and configuration.
    
    Returns:
        Tuple of (config, project_root) or (None, project_root) if config fails
    """
    # Add the project root to Python path more safely
    current_file = Path(__file__).resolve() if '__file__' in globals() else Path().resolve()
    project_root = current_file.parent.parent.parent
    
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Try to import and setup configuration
    try:
        from Module_2_LLM_basics.configs.config import get_config
        config = get_config()
        config.setup_logging()
        
        # Validate configuration
        if not config.validate():
            logging.warning("Configuration validation failed, proceeding with default values")
            
        return config, project_root
        
    except ImportError as e:
        # Fallback if config module is not available
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.warning(f"Could not import configuration module: {e}")
        logging.info("Using fallback configuration")
        return None, project_root

def get_safe_imports():
    """
    Get safe import statements for notebooks.
    
    Returns:
        Dictionary with imported modules and configuration
    """
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
    
    # Setup environment
    config, project_root = setup_notebook_environment()
    
    # Import project modules
    try:
        from Module_2_LLM_basics.src.loader import ArticleLoader
        from Module_2_LLM_basics.src.retriever import ArticleRetriever
    except ImportError as e:
        logging.error(f"Could not import project modules: {e}")
        logging.info("Make sure the project structure is correct and modules are in Python path")
        raise
    
    # Import external libraries
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
    
    # Configure paths and models
    if config:
        persist_directory = config.vectordb.persist_directory
        json_dir = config.data.json_data_dir
        embedding_model_name = config.retriever.default_embedding_model
        default_k = config.retriever.default_k
    else:
        # Fallback values
        persist_directory = 'docs/chroma/'
        json_dir = "../dataset_doc/train"
        embedding_model_name = "text-embedding-3-small"
        default_k = 5
    
    # Initialize models
    llm = ChatOpenAI(model='gpt-4o-mini')
    embeddings_model = OpenAIEmbeddings(model=embedding_model_name)
    
    # Print status information
    print(f"OpenAI API Key Loaded: {'OPENAI_API_KEY' in os.environ and bool(os.environ.get('OPENAI_API_KEY'))}")
    print(f"LLM Model Name: {llm.model_name}")
    print(f"Embeddings Model Name: {embeddings_model.model}")
    print(f"Using persist directory: {persist_directory}")
    print(f"Using JSON data directory: {json_dir}")
    print(f"Default retrieval k: {default_k}")
    
    return {
        'config': config,
        'project_root': project_root,
        'ArticleLoader': ArticleLoader,
        'ArticleRetriever': ArticleRetriever,
        'Chroma': Chroma,
        'glob': glob,
        'llm': llm,
        'embeddings_model': embeddings_model,
        'persist_directory': persist_directory,
        'json_dir': json_dir,
        'default_k': default_k,
        'MemorySaver': MemorySaver,
        'MessagesState': MessagesState,
        'StateGraph': StateGraph,
        'END': END,
        'ToolNode': ToolNode,
        'tools_condition': tools_condition,
        'tool': tool,
        'render_text_description_and_args': render_text_description_and_args,
        'SystemMessage': SystemMessage,
        'uuid4': uuid4,
        'display': display,
        'Markdown': Markdown
    }

# Convenience function for quick setup
def quick_setup():
    """Quick setup function for notebooks."""
    return get_safe_imports()