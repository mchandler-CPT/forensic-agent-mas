from pathlib import Path

class ForensicConfig:
    # Project Root (C:\DevProjects\digital_forensics_mas)
    ROOT_DIR = Path(__file__).parent.parent.parent
    
    # Environment Paths
    INPUT_DIR = ROOT_DIR / "data" / "input"
    OUTPUT_DIR = ROOT_DIR / "data" / "output"
    REPORT_PATH = OUTPUT_DIR / "forensic_manifest.csv"
    
    # Agent Settings
    POLLING_INTERVAL = 10  # seconds
    
    # Logging
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'