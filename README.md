# 🦅 AeroGuard: Autonomous Critical Incident Response AI

### *A Multi-Agent System for Wildfire Evacuation Routing*

![Python](https://img.shields.io/badge/Python-3.11-blue)
![AI](https://img.shields.io/badge/AI-LangGraph-orange)
![Model](https://img.shields.io/badge/Llama-3.1-purple)
![Frontend](https://img.shields.io/badge/Frontend-Streamlit-red)

## 📋 Project Overview
**AeroGuard** is a safety-critical AI system designed to assist Incident Commanders during wildfire emergencies. 

While most AI tools are passive chatbots, AeroGuard is an **Agentic System** that actively formulates and validates safety plans. It utilizes a **"Zero-Trust" Architecture** where one AI agent (The Commander) proposes a strategy, and a completely separate AI agent (The Auditor) validates it against hard physics data before any order is authorized.

**Key Capabilities:**
* **Self-Correction:** If the system proposes a dangerous route (e.g., moving downwind), the Auditor detects the physics violation and rejects the plan, forcing the Commander to replan automatically.
* **Global Simulation:** Capable of simulating scenarios in California (USA), New South Wales (Australia), and Attica (Greece).
* **Real-World Routing:** Integrates real highway topology for specific regions (e.g., CA-2, Great Western Hwy) rather than generic compass directions.

## ⚙️ System Architecture (The "Self-Healing" Loop)
The system operates on a cyclic graph (built with LangGraph) containing three specialized nodes:

1.  **🛰️ Sentry Node:** * Ingests geospatial telemetry (Simulated NASA VIIRS Thermal Data).
    * Calculates wind vectors and "Deadly Sectors" (Downwind).
2.  **🧠 Commander Node:** * Analyzes the topology and available escape routes.
    * Formulates a draft evacuation order (e.g., "Evacuate West via Big Tujunga Canyon Rd").
3.  **🛡️ Auditor Node (The Guardrail):** * Performs a strict Boolean check: *Does the draft plan move away from the smoke vector?*
    * **Pass:** The plan is signed with a cryptographic-style simulation ID.
    * **Fail:** The plan is rejected, and the cycle repeats with feedback.

## 🛠️ Tech Stack
* **Orchestration:** LangGraph (Stateful Multi-Agent Logic)
* **LLM Engine:** Llama 3.1 (Running locally via Ollama)
* **Frontend:** Streamlit (Reactive Python Dashboard)
* **Data Sources:** NASA FIRMS (Simulated Profile), Open-Meteo (Weather logic).

## 🚀 How to Run Locally

### Prerequisites
* Python 3.10+
* [Ollama](https://ollama.com/) installed and running.

### Installation
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/AeroGuard-AI.git](https://github.com/YOUR_USERNAME/AeroGuard-AI.git)
    cd AeroGuard-AI
    ```

2.  **Create a Virtual Environment (Optional but Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the Local Model:**
    Make sure Ollama is running, then pull the Llama 3 model:
    ```bash
    ollama pull llama3.1
    ```

5.  **Launch the Dashboard:**
    ```bash
    streamlit run app.py
    ```

## 📸 Interface
*(Add your screenshots here by dragging and dropping them into the GitHub editor)*

## ⚠️ Disclaimer
**SIMULATION ONLY.** This software is a portfolio project demonstrating Multi-Agent AI architecture. It uses simulated data profiles for the Angeles National Forest and other regions. It is **not** connected to live emergency alert systems and should not be used for real-world disaster response.

---
*Built by [Your Name] as a specialized portfolio project demonstrating autonomous system reliability.*