# Autonomous Forensic Multi-Agent System (MAS)

An intelligent, decoupled Multi-Agent System designed as a "Forensic First Responder" for post-attack evidence recovery. The system autonomously discovers suspicious files, verifies their integrity using cryptographic hashing, and maintains a persistent, stateful chain of custody.

## 🏗️ Architecture: BDI & Event-Driven
The system utilizes a **Belief-Desire-Intention (BDI)** model for agent autonomy and an **Observer Pattern (Event Bus)** for decoupled communication.

* **Collector Agent:** Scans target directories. It maintains **Persistent Beliefs** by synchronizing with historical manifests to prevent redundant processing.
* **Processor Agent:** Handles forensic integrity. It executes SHA-256 hashing to create a digital fingerprint of every discovered artifact.
* **Reporter Agent:** The "Evidence Clerk." It archives verified metadata into a formal, immutable forensic manifest.



---

## 🔍 Forensic Integrity & Chain of Custody
The system generates a formal manifest (`forensic_manifest.csv`) with the following "Expert" metadata:

| Field | Purpose | Forensic Value |
| :--- | :--- | :--- |
| **Timestamp** | Temporal logging | Establishes exactly when the evidence was secured. |
| **Agent_ID** | Accountability | Identifies which autonomous entity performed the processing. |
| **SHA256_Hash** | Integrity | Provides a mathematically unique fingerprint of the file. |
| **File_Size** | Redundancy | Secondary check against file tampering or corruption. |



---

## 🛠️ Tech Stack & Setup
* **Language:** Python 3.10+
* **Architecture:** BDI (Belief-Desire-Intention)
* **Libraries:** Pandas (Data management), Pytest (TDD/Testing)
* **Security:** SHA-256 (NIST-standard hashing)

### Installation
```powershell
# 1. Clone the repository
git clone [https://github.com/](https://github.com/)[your-username]/digital_forensics_mas.git

# 2. Install dependencies
pip install -r requirements.txt
```

### Running the System

```powershell
# Run the orchestrator from the project root
python -m src.main
```

## 📈 System Robustness & "Smart" Scanning

To ensure "Production Readiness" for this MSc-level implementation, the system incorporates the following features:

* **Idempotency & Persistence:** The **Collector Agent** is designed to rebuild its mental state from the `forensic_manifest.csv` on startup. This ensures that no file is ever processed twice across sessions, maintaining stateful awareness even after a system reboot.
* **Fault Tolerance:** The architecture enforces strict **Forensic Integrity**. A failure in the integrity check (Processor) correctly halts the pipeline, preventing unverified or "tainted" artifacts from being committed to the legal manifest.
* **Environment Isolation:** Centralized configuration via `ForensicConfig` allows for seamless deployment across varied forensic environments (Windows vs. Linux) without requiring code modifications.



---

## 🚀 Future Roadmap (Critical Evaluation)

As part of the iterative development and critical evaluation of this Multi-Agent System (MAS), several key extensions are proposed:

* **Asynchronous Parallelism:** Transitioning from a single-threaded polling loop to asynchronous processing to handle high-volume data environments efficiently.
* **Automated Quarantine:** Implementation of an `evidence_vault` agent that moves or isolates suspicious files (e.g., those with high entropy or unauthorized extensions) immediately after hashing.
* **Cloud Integrity:** Synchronizing manifests to a secure, remote location to prevent "tamper-and-delete" attacks by sophisticated adversaries.

---