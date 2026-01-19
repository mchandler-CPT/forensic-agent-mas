import time
from src.common.config import ForensicConfig as Config
from src.common.logger import get_agent_logger
from src.common.event_bus import EventBus
from src.agents.collector import CollectorAgent
from src.agents.processor import ProcessorAgent
from src.agents.reporter import ReporterAgent
from src.agents.vault import VaultAgent

# Initialize the primary system orchestrator logger
# This logger will record high-level system lifecycle events
logger = get_agent_logger("Orchestrator")

def main():
    """
    Orchestrator for the Autonomous Forensic Multi-Agent System.
    Integrates BDI agents with a centralized, file-based audit trail.
    """
    # 1. Initialize the Event Bus (The 'Observer' Hub)
    bus = EventBus()
    
    # 2. Prepare the Environment
    # Ensures all required directories for logs, metadata, and vaulting exist
    Config.INPUT_DIR.mkdir(parents=True, exist_ok=True)
    Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    Config.ROOT_DIR.joinpath("logs").mkdir(exist_ok=True)
    
    # 3. Instantiate Intelligent Agents
    # Each agent now consumes the centralized logger factory internally
    collector = CollectorAgent(
        bus, 
        Config.INPUT_DIR, 
        manifest_path=Config.REPORT_PATH
    )
    
    processor = ProcessorAgent(bus)
    reporter = ReporterAgent(bus, report_path=Config.REPORT_PATH)
    
    # Professional Pathing: Ensuring the vault resides within the data boundary
    vault_path = Config.ROOT_DIR / "data" / "evidence_vault"
    vault = VaultAgent(bus, vault_path)
    
    # 4. Wire Up The Forensic Pipeline (Observer Pattern)
    bus.subscribe("FILE_FOUND", processor.process_file)
    bus.subscribe("FILE_PROCESSED", reporter.record_evidence)
    bus.subscribe("FILE_PROCESSED", vault.archive_file)
    
    print("\n" + "="*60)
    print("  AUTONOMOUS FORENSIC PIPELINE: ACTIVE")
    print(f"  SCANNING: {Config.INPUT_DIR}")
    print(f"  LOGGING:  {Config.REPORT_PATH}")
    print(f"  AUDIT:    {Config.ROOT_DIR / 'logs' / 'agent_system.log'}")
    print("="*60 + "\n")
    
    logger.info("System Startup: Forensic pipeline initialized and agents online.")
    
    try:
        # 5. The Agent Lifecycle Loop
        while True:
            # The 'Sense' phase of the BDI Perceive-Think-Act loop
            collector.act()
            
            # Resource management via configurable polling
            time.sleep(Config.POLLING_INTERVAL)
            
    except KeyboardInterrupt:
        logger.warning("Shutdown signal detected. Finalizing audit logs.")
        print("\n[!] Shutdown sequence complete.")

if __name__ == "__main__":
    main()