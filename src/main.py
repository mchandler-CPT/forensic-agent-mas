import time
import logging
from pathlib import Path
from src.common.event_bus import EventBus
from src.agents.collector import CollectorAgent
from src.agents.processor import ProcessorAgent
from src.agents.reporter import ReporterAgent

# Configure logging to show the 'Hand-off' between agents
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # 1. Infrastructure Setup
    bus = EventBus()
    
    # Define environment - using absolute paths for the demo
    base_path = Path(__file__).parent.parent
    source_dir = base_path / "data" / "input"
    report_file = base_path / "data" / "output" / "forensic_manifest.csv"
    
    source_dir.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 2. Agent Initialization
    collector = CollectorAgent(bus, source_dir)
    processor = ProcessorAgent(bus)
    reporter = ReporterAgent(bus, report_path=report_file)
    
    # 3. The Forensic Pipeline (Observer Pattern)
    # Step A: When Collector finds a file, Processor is notified to hash it
    bus.subscribe("FILE_FOUND", processor.process_file)
    
    # Step B: When Processor finishes hashing, Reporter is notified to archive it
    bus.subscribe("FILE_PROCESSED", reporter.record_evidence)
    
    print("\n" + "="*60)
    print("  AUTONOMOUS FORENSIC PIPELINE ACTIVE")
    print(f"  TARGET: {source_dir}")
    print(f"  LOG:    {report_file}")
    print("="*60 + "\n")
    
    try:
        while True:
            # The BDI 'Heartbeat' - Collector perceives and acts
            collector.act()
            time.sleep(10) 
            
    except KeyboardInterrupt:
        print("\n[!] Shutdown signal received. Closing forensic logs.")

if __name__ == "__main__":
    main()