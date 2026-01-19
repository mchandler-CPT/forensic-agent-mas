import time
import logging
from src.common.config import ForensicConfig as Config
from src.common.event_bus import EventBus
from src.agents.collector import CollectorAgent
from src.agents.processor import ProcessorAgent
from src.agents.reporter import ReporterAgent

# Use the centralized log format
logging.basicConfig(level=logging.INFO, format=Config.LOG_FORMAT)

def main():
    # 1. Setup Infrastructure
    bus = EventBus()
    
    # 2. Ensure Environment Readiness
    # This fulfills the 'Production Readiness' requirement
    Config.INPUT_DIR.mkdir(parents=True, exist_ok=True)
    Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 3. Instantiate Agents using Config settings
    collector = CollectorAgent(bus, Config.INPUT_DIR)
    processor = ProcessorAgent(bus)
    reporter = ReporterAgent(bus, report_path=Config.REPORT_PATH)
    
    # 4. Wire Up Subscriptions
    bus.subscribe("FILE_FOUND", processor.process_file)
    bus.subscribe("FILE_PROCESSED", reporter.record_evidence)
    
    print("\n" + "="*60)
    print("  PRO-GRADE FORENSIC MAS STARTUP")
    print(f"  TARGET: {Config.INPUT_DIR}")
    print(f"  LOG:    {Config.REPORT_PATH}")
    print("="*60 + "\n")
    
    try:
        while True:
            # The BDI 'Heartbeat'
            collector.act()
            time.sleep(Config.POLLING_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n[!] Shutdown sequence initiated. Closing forensic logs.")

if __name__ == "__main__":
    main()