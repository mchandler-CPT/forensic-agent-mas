import time
import logging
from src.common.config import ForensicConfig as Config
from src.common.event_bus import EventBus
from src.agents.collector import CollectorAgent
from src.agents.processor import ProcessorAgent
from src.agents.reporter import ReporterAgent

# Configure professional logging using our centralized Config
logging.basicConfig(level=logging.INFO, format=Config.LOG_FORMAT)

def main():
    """
    Orchestrator for the Autonomous Forensic Multi-Agent System.
    This entry point initializes the infrastructure and wires agent communication.
    """
    # 1. Initialize the Event Bus (The 'Observer' Hub)
    # Rationale: Decouples agents to allow for scalability and independent failure.
    bus = EventBus()
    
    # 2. Prepare the Environment
    # Ensures the MAS can run autonomously in a 'Post-Attack' recovery scenario.
    Config.INPUT_DIR.mkdir(parents=True, exist_ok=True)
    Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 3. Instantiate Intelligent Agents
    # Each agent is a BDI entity with specific forensic responsibilities.
    collector = CollectorAgent(bus, Config.INPUT_DIR)
    processor = ProcessorAgent(bus)
    reporter = ReporterAgent(bus, report_path=Config.REPORT_PATH)
    
    # 4. Wire Up The Forensic Pipeline
    # Trigger 1: Collector -> Processor (Handoff for Integrity Verification)
    bus.subscribe("FILE_FOUND", processor.process_file)
    
    # Trigger 2: Processor -> Reporter (Handoff for Evidence Archiving)
    bus.subscribe("FILE_PROCESSED", reporter.record_evidence)
    
    print("\n" + "="*60)
    print("  AUTONOMOUS FORENSIC PIPELINE: ACTIVE")
    print(f"  SCANNING: {Config.INPUT_DIR}")
    print(f"  LOGGING:  {Config.REPORT_PATH}")
    print("="*60 + "\n")
    
    try:
        # 5. The Agent Lifecycle Loop
        # In a real-world MAS, agents operate in a continuous Perceive-Act loop.
        while True:
            # Collector acts as the 'Primary Sensor' for the environment
            collector.act()
            
            # Polling interval defined in Config to manage system resources
            time.sleep(Config.POLLING_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n[!] Shutdown signal detected. Finalizing manifest and closing agents.")

if __name__ == "__main__":
    main()