"""
Configuration module for the LLM basics project.

This module provides centralized configuration management for all components.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None


@dataclass
class ParserConfig:
    """Configuration for document parsing."""
    min_paragraph_length: int = 20
    encoding: str = "utf-8"
    ignored_labels: list = field(default_factory=lambda: ["equation", "figure"])
    

@dataclass
class RetrieverConfig:
    """Configuration for document retrieval."""
    default_k: int = 5
    max_k: int = 50
    default_embedding_model: str = "text-embedding-3-small"


@dataclass
class VectorDBConfig:
    """Configuration for vector database."""
    persist_directory: str = "docs/chroma/"
    collection_name: str = "docbank_articles"
    

@dataclass
class DataConfig:
    """Configuration for data paths and processing."""
    json_data_dir: str = "../dataset_doc/train"
    max_articles_to_process: Optional[int] = None
    

@dataclass
class AppConfig:
    """Main application configuration."""
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    parser: ParserConfig = field(default_factory=ParserConfig)
    retriever: RetrieverConfig = field(default_factory=RetrieverConfig)
    vectordb: VectorDBConfig = field(default_factory=VectorDBConfig)
    data: DataConfig = field(default_factory=DataConfig)
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables."""
        config = cls()
        
        # Update from environment variables if they exist
        if log_level := os.getenv("LOG_LEVEL"):
            config.logging.level = log_level
            
        if log_file := os.getenv("LOG_FILE"):
            config.logging.file_path = log_file
            
        if min_length := os.getenv("MIN_PARAGRAPH_LENGTH"):
            try:
                config.parser.min_paragraph_length = int(min_length)
            except ValueError:
                logging.warning(f"Invalid MIN_PARAGRAPH_LENGTH value: {min_length}")
                
        if default_k := os.getenv("DEFAULT_K"):
            try:
                config.retriever.default_k = int(default_k)
            except ValueError:
                logging.warning(f"Invalid DEFAULT_K value: {default_k}")
                
        if persist_dir := os.getenv("CHROMA_PERSIST_DIR"):
            config.vectordb.persist_directory = persist_dir
            
        if json_dir := os.getenv("JSON_DATA_DIR"):
            config.data.json_data_dir = json_dir
            
        if max_articles := os.getenv("MAX_ARTICLES"):
            try:
                config.data.max_articles_to_process = int(max_articles)
            except ValueError:
                logging.warning(f"Invalid MAX_ARTICLES value: {max_articles}")
        
        return config
    
    def setup_logging(self) -> None:
        """Setup logging based on configuration."""
        log_level = getattr(logging, self.logging.level.upper(), logging.INFO)
        
        handlers = [logging.StreamHandler()]
        if self.logging.file_path:
            # Ensure log directory exists
            log_path = Path(self.logging.file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(self.logging.file_path))
        
        logging.basicConfig(
            level=log_level,
            format=self.logging.format,
            handlers=handlers,
            force=True  # Override any existing configuration
        )
        
        logging.info("Logging configured successfully")
    
    def validate(self) -> bool:
        """Validate configuration values."""
        errors = []
        
        # Validate parser config
        if self.parser.min_paragraph_length < 0:
            errors.append("min_paragraph_length must be non-negative")
            
        # Validate retriever config
        if self.retriever.default_k <= 0:
            errors.append("default_k must be positive")
            
        if self.retriever.max_k <= 0:
            errors.append("max_k must be positive")
            
        if self.retriever.default_k > self.retriever.max_k:
            errors.append("default_k cannot be greater than max_k")
        
        # Validate paths
        if self.data.json_data_dir and not Path(self.data.json_data_dir).exists():
            errors.append(f"JSON data directory does not exist: {self.data.json_data_dir}")
        
        if errors:
            for error in errors:
                logging.error(f"Configuration validation error: {error}")
            return False
            
        logging.info("Configuration validation passed")
        return True


# Global configuration instance
config = AppConfig.from_env()


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config


def update_config(**kwargs) -> None:
    """Update global configuration with new values."""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            logging.warning(f"Unknown configuration key: {key}")