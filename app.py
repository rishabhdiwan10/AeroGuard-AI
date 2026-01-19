import streamlit as st
import pandas as pd
import time
import tools
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="AeroGuard Command",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    /* Telemetry Cards */
    .metric-container {
        background-color: #1e212b;
        border: 1px solid #30333d;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    
    /* Official Alert Card */
    .alert-card {
        background-color: #1b2e1e;
        border: 1px solid #4CAF50;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .alert-header {
        color: #4CAF50;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 10px;
        border-bottom: 1px solid #4CAF50;
        padding-bottom: 5px;
    }
    
    /* Fail Card */
    .fail-card {
        background-color: #2e1b1b;
        border: 1px solid #e74c3c;
        border-radius: 8px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. GLOBAL SCENARIO DATA (WITH REAL ROUTES) ---
SCENARIOS = {
    "Angeles National Forest, USA": {
        "lat": 34.24, "lon": -118.15, "default_wind": 270, "default_speed": 45, "intensity": "450K",
        # Real Highways in this area
        "routes": {
            "NORTH": "Angeles Forest Hwy towards Palmdale",
            "SOUTH": "CA-2 South towards Glendale",
            "WEST": "Big Tujunga Canyon Rd towards Sunland",
            "EAST": "CA-39 towards Crystal Lake",
            "NORTH-WEST": "Soledad Canyon Rd towards Santa Clarita",
            "SOUTH-EAST": "San Gabriel Canyon Rd towards Azusa",
            "SOUTH-WEST": "I-210 West towards Pasadena",
            "NORTH-EAST": "Pearblossom Hwy towards Victorville"
        }
    },
    "Blue Mountains, Australia (NSW)": {
        "lat": -33.71, "lon": 150.31, "default_wind": 90, "default_speed": 60, "intensity": "500K",
        "routes": {
            "NORTH": "Bells Line of Road towards Kurrajong",
            "SOUTH": "Great Western Hwy towards Penrith",
            "WEST": "Great Western Hwy towards Lithgow",
            "EAST": "M4 Motorway towards Sydney",
            "NORTH-WEST": "Chifley Rd towards Clarence",
            "SOUTH-EAST": "Mulgoa Rd towards Penrith",
            "SOUTH-WEST": "Jenolan Caves Rd towards Oberon",
            "NORTH-EAST": "Hawkesbury Rd towards Springwood"
        }
    },
    "Attica Region, Greece": {
        "lat": 38.04, "lon": 23.86, "default_wind": 315, "default_speed": 55, "intensity": "420K",
        "routes": {
            "NORTH": "E75 Highway towards Lamia",
            "SOUTH": "Attiki Odos towards Athens Center",
            "WEST": "Leoforos Kifisias towards Marousi",
            "EAST": "Marathonos Avenue towards Nea Makri",
            "NORTH-WEST": "Tatoiou Avenue towards Acharnes",
            "SOUTH-EAST": "Mesogeion Avenue towards Airport",
            "SOUTH-WEST": "Kymis Avenue towards Galatsi",
            "NORTH-EAST": "Dionysou Avenue towards Dionysos"
        }
    }
}

# --- 3. HELPER FUNCTIONS ---
def get_cardinal(deg):
    dirs = ["NORTH", "NORTH-EAST", "EAST", "SOUTH-EAST", "SOUTH", "SOUTH-WEST", "WEST", "NORTH-WEST"]
    idx = int((deg + 22.5) / 45.0) & 7
    return dirs[idx]

# --- 4. SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=60)
    st.title("AeroGuard")
    st.caption("Autonomous Critical Incident Response")
    st.markdown("---")
    
    with st.expander("ℹ️ Mission Briefing", expanded=True):
        st.markdown("""
        **Objective:** Deploy autonomous multi-agent AI to coordinate evacuations in global wildfire zones.
        **Core Architecture:** Sentry (Data), Commander (Strategy), Auditor (Safety).
        """)
        
    st.markdown("---")
    st.markdown("### 📍 Operation Theater")
    
    # SCENARIO SELECTOR
    selected_scenario_name = st.selectbox("Select Active Sector:", list(SCENARIOS.keys()))
    scenario_data = SCENARIOS[selected_scenario_name]
    
    # --- AUTO-RESET LOGIC (Fixes the Premature Start Bug) ---
    if 'last_scenario' not in st.session_state:
        st.session_state['last_scenario'] = selected_scenario_name
        
    if st.session_state['last_scenario'] != selected_scenario_name:
        st.session_state['active'] = False  # STOP the simulation
        st.session_state['last_scenario'] = selected_scenario_name # Update memory
        st.rerun() # Refresh page to show "Standby" state

    st.markdown("### 🎛️ Environmental Controls")
    wind_dir = st.slider("Wind Source (Degrees)", 0, 360, scenario_data["default_wind"], help="Direction wind is blowing FROM.")
    wind_spd = st.slider("Wind Velocity (km/h)", 0, 100, scenario_data["default_speed"])
    
    st.markdown("---")
    if st.button("🔴 INITIATE PROTOCOL", type="primary", use_container_width=True):
        st.session_state['active'] = True

# --- 5. MAIN DASHBOARD ---
st.title("🦅 AeroGuard Command Center")

if not st.session_state.get('active', False):
    st.info(f"⚠️ **STANDBY MODE:** Sector '{selected_scenario_name}' loaded. Waiting for command authorization.")
    
    # Show Map in Standby
    st.map(pd.DataFrame({'lat': [scenario_data["lat"]], 'lon': [scenario_data["lon"]]}), zoom=9, use_container_width=True)
    st.stop()

# --- 6. ACTIVE TELEMETRY ---
# Calculate Directions
safe_cardinal = get_cardinal(wind_dir) 
bad_cardinal = get_cardinal((wind_dir + 180) % 360)

# Lookup Specific Routes
safe_route = scenario_data["routes"].get(safe_cardinal, f"Evacuate {safe_cardinal} (General Route)")
bad_route = scenario_data["routes"].get(bad_cardinal, f"Evacuate {bad_cardinal} (General Route)")

col_map, col_data = st.columns([2, 1])

with col_map:
    st.subheader("📍 Geospatial Grid")
    st.map(pd.DataFrame({'lat': [scenario_data["lat"]], 'lon': [scenario_data["lon"]]}), zoom=10, use_container_width=True)

with col_data:
    st.subheader("📊 Sensor Telemetry")
    st.markdown(f"""
    <div class="metric-container">
        <strong style="color: #e74c3c">🔥 THERMAL SIGNATURE</strong><br>
        Intensity: {scenario_data['intensity']}<br>
        Status: Uncontained
    </div>
    <div class="metric-container">
        <strong style="color: #3498db">💨 ATMOSPHERICS</strong><br>
        Wind Speed: {wind_spd} km/h<br>
        Source Vector: {wind_dir}° ({safe_cardinal})
    </div>
    """, unsafe_allow_html=True)

# --- 7. AGENT WORKFLOW ---
st.markdown("---")
st.subheader("🤖 Autonomous Response Chain")

llm = ChatOllama(model="llama3.1", temperature=0.0) 
final_plan = None

with st.status("Orchestrating Agents...", expanded=True) as status:
    
    # STEP 1: COMMANDER
    st.write("🧠 **Commander Node:** analyzing topological routes...")
    time.sleep(1)
    
    # SMART PROMPT: We feed the REAL ROUTES to the AI options
    prompt = f"""
    [ROLE] Incident Commander.
    [TELEMETRY] Wind Source: {wind_dir}° ({safe_cardinal}).
    [PROTOCOL] Evacuate UPWIND towards the wind source.
    [AVAILABLE ROUTES]
    - OPTION A: {safe_route}
    - OPTION B: {bad_route}
    
    [TASK] Select the correct evacuation route.
    OUTPUT: Return ONLY the text of the correct Option (do not include "Option A").
    """
    commander_msg = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    st.info(f"Draft Strategy: {commander_msg}")
    
    # STEP 2: AUDITOR
    st.write("🛡️ **Auditor Node:** Validating against Zero-Trust Safety Protocols...")
    
    audit_prompt = f"""
    [ROLE] Safety Auditor.
    [INPUT] "{commander_msg}"
    [SAFE VECTOR] "{safe_cardinal}"
    
    [LOGIC]
    - Does the input mention "{safe_cardinal}" or the correct highway? -> APPROVE
    - Otherwise -> REJECT
    
    OUTPUT: Return ONLY "APPROVED" or "REJECTED".
    """
    auditor_msg = llm.invoke([HumanMessage(content=audit_prompt)]).content.strip()
    
    if "APPROVED" in auditor_msg.upper():
        st.success("✅ Safety Protocols Verified.")
        status.update(label="Mission Complete: Strategy Authorized", state="complete", expanded=False)
        final_plan = commander_msg
    else:
        st.error(f"❌ Critical Safety Failure: {auditor_msg}")
        status.update(label="Mission Aborted: Safety Lock Engaged", state="error", expanded=True)

# --- 8. FINAL DIRECTIVE ---
st.markdown("---")
st.subheader("📢 Operational Directive")

if final_plan:
    st.markdown(f"""
    <div class="alert-card">
        <div class="alert-header">✅ EVACUATION ORDER AUTHORIZED</div>
        <p><strong>SECTOR:</strong> {selected_scenario_name}</p>
        <p><strong>AUTHORIZATION ID:</strong> SIM-{int(time.time())}</p>
        <h2 style="margin-top: 15px; color: white;">ACTION: {final_plan.upper().replace('OPTION A:', '').replace('OPTION B:', '')}</h2>
        <p><strong>STRATEGIC RATIONALE:</strong> Atmospheric data indicates wind source from {safe_cardinal}. Proceeding via this route maintains separation from the advancing thermal front.</p>
        <hr style="border-color: #4CAF50;">
        <small><i>Route verified by AeroGuard Autonomous Safety System.</i></small>
    </div>
    """, unsafe_allow_html=True)
    st.balloons()
else:
    st.markdown("""
    <div class="fail-card">
        <h3>❌ AUTOMATIC SAFETY LOCKDOWN</h3>
        <p>The system detected a high-risk logical conflict in the evacuation path.</p>
        <p><strong>ACTION:</strong> FALLBACK TO MANUAL RADIO COMMAND.</p>
    </div>
    """, unsafe_allow_html=True)