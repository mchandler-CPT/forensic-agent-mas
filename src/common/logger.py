import logging
import sys
from pathlib import Path
from src.common.config import ForensicConfig as Config

def get_agent_logger(agent_name):
    logger = logging.getLogger(agent_name)
    
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.INFO)
    
    # FORCED PATH: Root -> data -> logs
    # Using .resolve() handles the 'python -m' execution context
    log_dir = Config.ROOT_DIR.resolve() / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "agent_system.log"
    
    # This will show up in PowerShell immediately
    print(f"[*] {agent_name} initializing audit trail at: {log_file}")
    
    try:
        # File Handler (Append mode for forensic audit)
        fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        fh.setLevel(logging.INFO)
        
        # Console Handler (Live view)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        logger.propagate = False
        
    except Exception as e:
        print(f"CRITICAL ERROR: Logger could not write to {log_file}: {e}")
    
    return logger