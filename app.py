import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import requests
import re
import time
import math
from streamlit_drawable_canvas import st_canvas

# --- Checklist Database (全機体統合) ---
cl_db = {
    "A350": {
        "COCKPIT PREP": ["PARKING BRAKE - SET", "ALL BATTERY SWITCH - ON", "EXTERNAL POWER - PUSH", "ADIRS (1, 2, 3) - NAV", "CREW SUPPLY - ON", "PACKS - AUTO", "NAV LIGHTS - ON", "LOGO LIGHTS - ON", "APU - MASTER-START", "NO SMOKING - AUTO", "NO MOBILE - AUTO", "EMERGENCY LIGHTS - ARMED", "FLIGHT DIRECTORS - ON", "ALTIMETERS - SET", "MCDU - SETUP", "FLT CTL PAGE - CHECK"],
        "BEFORE START": ["WINDOWS/DOORS - CLOSED", "BEACON - ON", "THRUST LEVERS - IDLE", "FUEL PUMPS - ON", "TRANSPONDER - AS REQ"],
        "AFTER START": ["ENGINE MODE SELECTOR - NORM", "PITCH TRIM - SET", "AUTOBRAKE - MAX", "FLAPS - SET", "GND SPOILERS - ARMED", "APU - OFF", "FLIGHT CONTROLS - CHECKED", "RUDDER TRIM - ZERO", "ANTI-ICE - AS REQ"],
        "TAXI/TAKEOFF": ["GROUND EQUIPMENT - CLEAR", "NOSEWHEEL LIGHTS - TAXI", "BRAKES - CHECK", "AUTO THRUST - BLUE", "TCAS - TA/RA", "PACKS - OFF/ON"],
        "CRUISE": ["ALTIMETERS - STD", "ANTI-ICE - AS REQ", "ECAM MEMO - CHECKED"],
        "DESCENT/APPROACH": ["CABIN CREW - ADVISED", "ND TERRAIN - AS REQ", "APPROACH BUTTON - ARM", "APPR PHASE (MCDU) - ACTIVATE", "LANDING GEAR - DOWN"],
        "LANDING": ["GND SPOILERS - ARM", "ENG MODE SELECTOR - AS REQ", "AUTOBRAKE - AS REQ", "FLAPS - SET LDG", "GO AROUND ALTITUDE - SET", "ECAM MEMO - LDG NO BLUE"],
        "SHUTDOWN/SECURE": ["PARKING BRAKE - SET", "APU - START", "ENG 1 & 2 MASTER - OFF", "BEACON LIGHTS - OFF", "FLIGHT DIRECTORS - OFF", "PASSENGER SIGNS - OFF", "SLIDES - DISARM", "FUEL PUMPS - OFF", "DOORS - OPEN", "ADIRS - OFF", "EMERGENCY LIGHTS - OFF", "NAV/LOGO LIGHTS - OFF", "EXTERNAL POWER - OFF", "BATTERY - OFF"]
    },
    "B787": {
        "ELECTRICAL POWERUP": ["SERVICE INTERPHONE - OFF", "BACKUP WINDOW HEAT - ON", "PRIMARY WINDOW HEAT - ON", "ENGINE PRIMARY PUMP L&R - ON", "C1 & C2 ELEC PUMP - OFF", "L & R DEMAND PUMP - OFF", "SEAT BELT SIGNS - ON", "APU FIRE PANEL - SET", "CARGO FIRE ARM - NORM", "ENGINE EEC MODE - NORM", "FUEL JETTISON - OFF", "WING/ENGINE ANTI-ICE - AUTO"],
        "BEFORE START": ["FLIGHT DECK DOOR - CLOSED/LOCKED", "PASSENGER SIGNS - ON", "MCP - SET", "FMS - COMPLETED", "BEACON - ON"],
        "AFTER START/TAXI": ["FLAPS - SET", "AUTOBRAKE - RTO", "FLIGHT CONTROLS - CHECKED"],
        "CLIMB/CRUISE": ["LANDING GEAR - UP", "FLAPS - UP", "ALTIMETERS - STD", "ANTI-ICE - AS REQ"],
        "DESCENT": ["PRESSURIZATION (LDG ALT) - SET", "RECALL - CHECKED", "AUTOBRAKE - SET", "LANDING DATA (VREF) - VERIFY", "APPROACH BRIEFING - COMPLETE"],
        "APPROACH/LANDING": ["ALTIMETER - RESET TO LOCAL", "SPEED - 250 KIAS (BELOW 10k)", "LANDING LIGHTS - ON", "SEAT BELTS - ON"],
        "SHUTDOWN/POWER DOWN": ["PARKING BRAKE - SET", "APU - VERIFY RUNNING", "FUEL CONTROL SWITCHES - CUTOFF", "SEAT BELT SIGNS - OFF", "FUEL PUMPS - OFF", "BEACON LIGHT - OFF", "IRS SELECTORS - OFF", "FD DOOR POWER - OFF"]
    },
    "A320/321": {
        "COCKPIT PREP": ["GEAR PINS and COVERS - REMOVED", "FUEL QUANTITY - KG CHECK", "SIGNS - ON/AUTO", "ADIRS - NAV", "BARO REF - SET (BOTH)"],
        "BEFORE START": ["PARKING BRAKE - SET", "T.O SPEEDS & THRUST - BOTH SET", "WINDOWS/DOORS - CLOSED", "BEACON - ON"],
        "AFTER START": ["APU - OFF", "Y ELEC PUMP - OFF", "ANTI ICE - AS REQ", "PITCH TRIM - SET", "RUDDER TRIM - ZERO"],
        "APPROACH": ["BARO REF - SET", "SEAT BELTS - ON", "MINIMUM - SET", "ENG MODE SEL - AS REQ"],
        "LANDING": ["G/A ALTITUDE - SET", "CABIN CREW - ADVISED", "ECAM MEMO - LDG NO BLUE", "LDG GEAR - DOWN", "SPLRS - ARM", "FLAPS - SET"],
        "PARKING/SECURE": ["PARKING BRAKE - SET", "ENGINES - OFF", "FUEL PUMPS - OFF", "ADIRS - OFF", "EXT PWR - AS REQ"]
    },
    "B777": {
        "PREFLIGHT": ["ADIRU Switch - ON", "Emergency Exit Lights - ARMED", "Hydraulic Panel - SET", "Electrical Panel - SET", "Packs - ON", "FMC - SETUP"],
        "BEFORE START": ["Flight Deck Door - CLOSED", "Passenger Signs - ON", "MCP - SET", "Takeoff Speeds - SET", "Beacon - ON"],
        "AFTER START/TAXI": ["Anti-ice - AS REQ", "Recall - CHECKED", "Autobrake - RTO", "Flaps - SET", "Flight Controls - CHECKED"],
        "BEFORE TAKEOFF": ["Transponder - TA/RA", "Strobe Lights - ON"],
        "CRUISE": ["Altimeters - STD", "FMC/Fuel - CHECKED"],
        "DESCENT/APPROACH": ["Altimeters - QNH SET", "Landing Data - SET", "Autobrake - SET"],
        "SHUTDOWN": ["Hydraulic Panel - SET", "Fuel Pumps - OFF", "Flaps - UP", "Parking Brake - AS REQ", "Fuel Control Switches - CUTOFF", "Weather Radar - OFF"],
        "SECURING": ["ADIRU Switch - OFF", "Emergency Exit Lights - OFF", "Packs Switches - OFF", "APU - OFF"]
    },
    "B767": {
        "PREFLIGHT": ["Oxygen - TESTED", "IRS - OFF TO NAV", "HYDRAULIC PANEL - SET", "WINDOW HEAT - ON", "THROTTLES - IDLE", "GEAR PIN - REMOVED", "PARKING BRAKE - SET"],
        "BEFORE START": ["FUEL - KGS/PUMPS ON", "WINDOWS - CLOSED/LOCKED", "PASSENGER SIGNS - ON", "DOORS - CLOSED & ARMED"],
        "AFTER START": ["PROBE HEAT - ON", "ANTI-ICE - AS REQ", "ISOLATION VALVE - OFF", "FUEL CTRL - RUN & LOCKED"],
        "BEFORE TAXI": ["RECALL - CHECKED", "FLT CTRLS - CHECKED", "FLAPS - SET", "AUTOBRAKE - RTO"],
        "AFTER TAKEOFF": ["LANDING GEAR - UP & OFF", "FLAPS - UP", "ALTIMETERS - SET STD"],
        "DESCENT/APPROACH": ["LDG ALT - SET", "PASSANGER SIGNS - ON", "RECALL - CHECKED", "AUTOBRAKE - SET", "VREF/MINIMUMS - SET", "ALTIMETERS - QNH SET"],
        "LANDING": ["CABIN - SECURED", "SPEEDBRAKE - ARMED", "LANDING GEAR - DOWN", "FLAPS - SET"],
        "AFTER LANDING": ["ANTI-ICE - AS REQ", "APU - STARTED", "AUTOBRAKE - OFF", "SPEEDBRAKE - DOWN", "FLAPS - UP", "WEATHER RADAR - OFF"]
    },
    "A330": {
        "COCKPIT PREP": ["GEAR PINS & COVERS - REMOVED", "FUEL QUANTITY - CHECK", "SEAT BELTS - ON", "ADIRS - NAV", "BARO REF - BOTH SET"],
        "BEFORE START": ["T.O SPEEDS & THRUST - BOTH SET", "WINDOWS - CLOSED", "BEACON - ON", "PARKING BRAKE - SET"],
        "AFTER START": ["ANTI ICE - AS REQ", "ECAM STATUS - CHECKED", "PITCH TRIM - SET", "RUDDER TRIM - CHECKED"],
        "APPROACH": ["BARO REF - BOTH SET", "SEAT BELTS - ON", "MINIMUM - SET", "AUTO BRAKE - SET", "ENG START SEL - AS REQ"],
        "LANDING": ["ECAM MEMO - LDG NO BLUE", "GEAR - DOWN", "FLAPS - SET"],
        "AFTER LANDING": ["RADAR & PRED W/S - OFF", "SPOILERS - DISARM", "FLAPS - RETRACT", "APU - START"],
        "PARKING": ["PARKING BRAKE/CHOCKS - SET", "ENGINES - OFF", "FUEL PUMPS - OFF"]
    },
    "HondaJet": {
        "CDU SETUP": ["Database Status - CONNECT", "Avionics Settings - AS DESIRED", "Flight Plan - ENTER/VERIFY"],
        "BEFORE START": ["ATC Clearance - OBTAIN", "Transponder - SQUAWK SET", "Alt Select - SET CLEARED ALT", "Parking Brake - SET", "Battery - ON", "External Power - AS REQ"],
        "ENGINE START": ["Doors - CLOSED", "Parking Brake - SET", "CAS Messages - REVIEW", "Elec Volts - MIN 23.5V", "Engine Start Button - PUSH"],
        "AFTER START/TAXI": ["External Power - DISCONNECT", "Lights - AS REQ", "Flaps - TAKE OFF", "Trim - SET (GREEN)"],
        "CRUISE": ["Altimeter - STD", "Ice Protection - AS REQ", "Fuel - MONITOR"],
        "LANDING": ["Landing Gear - DOWN & 3 GREEN", "Flaps - LDG", "Yaw Damper - OFF @50ft", "Throttles - IDLE @Threshold"],
        "SHUTDOWN": ["Parking Brake - SET", "Engines - OFF", "Electrical - OFF"]
    }
}

# --- 1. Page Configuration ---
st.set_page_config(page_title="EFBPro | Flight Portal", layout="wide")

# --- Mode Persistence ---
if 'efb_mode' not in st.session_state: st.session_state['efb_mode'] = "AIRBUS"

# --- Styling Logic (Design Switch) ---
if st.session_state['efb_mode'] == "BOEING":
    # Boeing UI (image_b16fa5.jpg 風)
    accent_color = "#3a86ff"
    bg_color = "#1a1c1e"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg_color}; color: #d1d2d3; }}
        /* Sidebar layout for Boeing */
        [data-testid="stSidebar"] {{ 
            background-color: #2c2f33 !important; 
            border-right: 2px solid #444; 
            min-width: 280px !important;
        }}
        /* Boeing style buttons (Rectangular, Grey) */
        div[role="radiogroup"] > label {{
            background-color: #3e4247 !important;
            border: 1px solid #555 !important;
            color: #fff !important;
            border-radius: 2px !important;
            padding: 15px !important;
            margin-bottom: 8px !important;
            text-align: center;
            font-family: sans-serif;
            text-transform: uppercase;
            font-size: 0.9em;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.1);
        }}
        div[role="radiogroup"] > label[data-checked="true"] {{
            background-color: #1a1c1e !important;
            border: 2px solid {accent_color} !important;
            color: {accent_color} !important;
            font-weight: bold;
        }}
        /* Main Container setup */
        .main-container {{
            background-color: #000000;
            border: 10px solid #4a4d52;
            border-radius: 15px;
            padding: 20px;
            min-height: 80vh;
        }}
        /* Boeing Header */
        .boeing-header {{
            text-align: center;
            border-bottom: 1px solid #444;
            padding-bottom: 10px;
            margin-bottom: 20px;
            color: #fff;
            font-weight: bold;
            letter-spacing: 2px;
        }}
        </style>
        """, unsafe_allow_html=True)
else:
    # Airbus UI
    accent_color = "#1DB954"
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: #FFFFFF; }
        h1, h2, h3, p, label, .stMarkdown { color: #FFFFFF !important; }
        .stTextInput>div>div>input { background-color: #FFFFFF !important; color: #000000 !important; border-radius: 4px !important; }
        .stButton>button { background-color: #1DB954 !important; color: #FFFFFF !important; border-radius: 4px !important; font-weight: bold; width: 100%; border: none; }
        [data-testid="stSidebar"] { background-color: #121212; border-right: 1px solid #282828; min-width: 350px !important; }
        .stTabs [data-baseweb="tab-list"] { position: static !important; background-color: transparent !important; border-bottom: 1px solid #282828; }
        div[role="radiogroup"] > label > div:first-child { display: none !important; }
        div[role="radiogroup"] > label {
            background-color: #1a1a1a !important; border: 1px solid #333 !important;
            padding: 12px 20px !important; border-radius: 4px !important; margin-bottom: 6px !important;
            width: 100% !important; transition: all 0.2s ease !important; cursor: pointer !important;
        }
        div[role="radiogroup"] > label:hover { border-color: #1DB954 !important; background-color: #252525 !important; }
        div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #252525 !important; border-left: 5px solid #1DB954 !important;
            color: #1DB954 !important; font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)

# --- 2. Persistence & Session State ---
DB_FILE, LINK_FILE, POS_FILE = "pilot_logbook.json", "quick_links.json", "pilot_positions.json"
SB_USER = "906331" 

if 'authenticated' not in st.session_state: st.session_state['authenticated'] = False
if 'sb_json' not in st.session_state: st.session_state['sb_json'] = None
if 'sw_running' not in st.session_state: st.session_state['sw_running'] = False
if 'sw_start_time' not in st.session_state: st.session_state['sw_start_time'] = 0
if 'timer_end' not in st.session_state: st.session_state['timer_end'] = None

# --- Data Load ---
if os.path.exists(POS_FILE):
    with open(POS_FILE, "r", encoding="utf-8") as f: p_pos = json.load(f)
else:
    p_pos = {"ANA": "RJTT", "JAL": "RJTT", "HDJT": "RJTT", "Delta": "KATL", "Lufthansa": "EDDF"}

default_links = [
    {"name": "ATIS GURU", "url": "https://atis.guru/"},
    {"name": "TRANSITION ALT LIST", "url": "https://docs.google.com/spreadsheets/d/1uTvrw-5uoGPuzGyB8lEkhyn7TO_HaZQ6WB-5N6nH-NM/edit?gid=1698518120#gid=1698518120"},
    {"name": "SIMBRIEF", "url": "https://www.simbrief.com/system/dispatch.php"},
    {"name": "NAVIGRAPH", "url": "https://charts.navigraph.com/"},
    {"name": "FAA NOTAM SEARCH", "url": "https://notams.aim.faa.gov/notamSearch/nsapp.html#/"}
]

if os.path.exists(LINK_FILE):
    with open(LINK_FILE, "r", encoding="utf-8") as f: quick_links = json.load(f)
else:
    quick_links = default_links

# --- 3. Login Logic ---
if not st.session_state['authenticated']:
    st.title("EFBPro SYSTEM ACCESS")
    if st.text_input("ENTER ACCESS CODE", type="password") == "3910":
        st.session_state['authenticated'] = True
        st.rerun()
else:
    # --- UI LAYOUT START ---
    if st.session_state['efb_mode'] == "BOEING":
        # Boeing Mode Left Menu Sidebar
        with st.sidebar:
            st.markdown("<h2 style='text-align:center;'>EFB MENU</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-size:0.8em;'>USER: {SB_USER}</p>", unsafe_allow_html=True)
            st.markdown("---")
            menu = st.radio("MAIN FUNCTIONS", ["OFP", "PILOT LOCATIONS", "WEATHER (METAR/ATIS)", "LOG", "TIMERS", "PAD", "T/D CALC", "TURN RADIUS", "UNIT CONVERTER", "X-WIND CALC", "VATSIM TRAFFIC"])
            st.markdown("---")
            if st.button("SWITCH TO AIRBUS"):
                st.session_state['efb_mode'] = "AIRBUS"
                st.rerun()
            for link in quick_links:
                st.markdown(f'<a href="{link["url"]}" target="_blank" style="color:#888; text-decoration:none; font-size:0.8em; display:block; margin:5px 0;">> {link["name"]}</a>', unsafe_allow_html=True)

        # Content Area inside the "Screen" frame
        st.markdown(f'<div class="boeing-header">{menu}</div>', unsafe_allow_html=True)
    else:
        # Airbus Mode Sidebar
        with st.sidebar:
            st.title("EFBPro")
            st.markdown(f"**USER ID:** `{SB_USER}`")
            st.markdown("---")
            s_tab1, s_tab2 = st.tabs(["LINKS", "TOOLS"])
            with s_tab1:
                for link in quick_links:
                    st.markdown(f'<a href="{link["url"]}" target="_blank" style="color:{accent_color}; text-decoration:none; font-weight:bold; display:block; margin:5px 0;">{link["name"]}</a>', unsafe_allow_html=True)
            with s_tab2:
                menu = st.radio("SELECT TOOL", ["PILOT LOCATIONS", "TIMERS", "OFP", "T/D CALC", "TURN RADIUS", "PAD", "WEATHER (METAR/ATIS)", "LOG", "UNIT CONVERTER", "X-WIND CALC", "VATSIM TRAFFIC"])
            
            if st.button("SWITCH TO BOEING"):
                st.session_state['efb_mode'] = "BOEING"
                st.rerun()

    # --- MAIN CONTENT TABS ---
    main_tab1, main_tab2, main_tab3 = st.tabs(["MAIN TOOLS", "CHECKLIST", "MAINTENANCE"])

    with main_tab1:
        if menu == "PILOT LOCATIONS":
            st.subheader("PILOT LOCATIONS")
            cols = st.columns(len(p_pos))
            for i, (airline, icao) in enumerate(p_pos.items()):
                new_icao = cols[i].text_input(f"{airline}", value=icao).upper()
                if new_icao != icao:
                    p_pos[airline] = new_icao
                    with open(POS_FILE, "w", encoding="utf-8") as f: json.dump(p_pos, f)
                    st.rerun()

        elif menu == "TIMERS":
            st.subheader("FLIGHT TIMERS")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### STOPWATCH")
                if st.button("START SW"):
                    st.session_state['sw_start_time'] = time.time()
                    st.session_state['sw_running'] = True
                if st.button("RESET SW"):
                    st.session_state['sw_running'] = False
                    st.session_state['sw_start_time'] = 0
                if st.session_state['sw_running']:
                    st.code(f"SW: {time.strftime('%H:%M:%S', time.gmtime(time.time() - st.session_state['sw_start_time']))}")
            with c2:
                st.markdown("### COUNTDOWN")
                t_min = st.number_input("MINUTES", 1, 180, 15)
                if st.button("SET TIMER"): st.session_state['timer_end'] = time.time() + (t_min * 60)
                if st.session_state['timer_end']:
                    rem = st.session_state['timer_end'] - time.time()
                    if rem > 0: st.metric("REMAINING", time.strftime('%H:%M:%S', time.gmtime(rem)))
                    else: st.warning("TIME UP!"); st.session_state['timer_end'] = None

        elif menu == "OFP":
            st.subheader("SIMBRIEF OFP & PERFORMANCE")
            if st.button("FETCH FROM SIMBRIEF"):
                res = requests.get(f"https://www.simbrief.com/api/xml.fetcher.php?userid={SB_USER}&json=1")
                if res.status_code == 200:
                    data = res.json()
                    if "params" in data:
                        st.session_state['sb_json'] = data
                        st.success("OFP & PERFORMANCE DATA IMPORTED")
                        st.rerun()
            
            if st.session_state.get('sb_json'):
                sb = st.session_state['sb_json']
                to_data = sb.get('takeoff', {})
                v1, vr, v2 = to_data.get('v1', '--'), to_data.get('vr', '--'), to_data.get('v2', '--')
                trim = to_data.get('trim', 'N/A')
                tow = sb.get('weights', {}).get('est_takeoff_weight', '0')

                st.markdown(f"""
                <div style="background: #111; padding: 20px; border-radius: 5px; border-left: 5px solid {accent_color}; margin-bottom: 20px;">
                    <p style="color: #888; margin: 0; font-size: 0.9em;">TAKEOFF PERFORMANCE</p>
                    <div style="display: flex; justify-content: space-around; text-align: center; padding: 15px 0;">
                        <div><div style="color:#888; font-size:0.8em;">V1</div><h1 style="margin:0; color:{accent_color};">{v1}</h1></div>
                        <div><div style="color:#888; font-size:0.8em;">VR</div><h1 style="margin:0; color:{accent_color};">{vr}</h1></div>
                        <div><div style="color:#888; font-size:0.8em;">V2</div><h1 style="margin:0; color:{accent_color};">{v2}</h1></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                info_col1, info_col2, info_col3 = st.columns(3)
                info_col1.metric("CALLSIGN", sb.get('atc', {}).get('callsign', "N/A"))
                info_col2.metric("TOW", f"{int(tow)/1000:.1f} T")
                info_col3.metric("DEST", sb.get('destination', {}).get('icao_code', "N/A"))

        elif menu == "T/D CALC":
            st.subheader("TOP OF DESCENT CALCULATOR")
            c1, c2, c3 = st.columns(3)
            curr_alt = c1.number_input("Current Alt (ft)", 0, 45000, 35000)
            target_alt = c2.number_input("Target Alt (ft)", 0, 45000, 3000)
            gs = c3.number_input("Ground Speed (kt)", 100, 600, 400)
            dist = ((curr_alt - target_alt) / 1000) * 3
            vs = gs * 5
            st.metric("Start Descent at", f"{dist:.1f} NM from Target")
            st.metric("Required VS", f"-{vs} fpm")

        elif menu == "TURN RADIUS":
            st.subheader("TURN RADIUS CALCULATOR")
            c1, c2 = st.columns(2)
            gs = c1.number_input("Ground Speed (KT)", 50, 600, 200)
            bank = c2.number_input("Bank Angle (deg)", 10, 45, 25)
            radius = (gs**2) / (11.26 * math.tan(math.radians(bank)))
            st.metric("Turn Radius", f"{radius:.2f} ft")

        elif menu == "PAD":
            st.subheader("FLIGHT MEMO / SCRATCH PAD")
            c1, c2 = st.columns([1, 3])
            draw_mode = c1.selectbox("TOOL", ["freedraw", "transform"])
            stroke_color = c1.selectbox("COLOR", ["#FFFFFF", "#FF4B4B", "#121212"])
            st_canvas(fill_color="rgba(255, 165, 0, 0.3)", stroke_width=3, stroke_color=stroke_color, background_color="#121212", height=400, drawing_mode=draw_mode, key="canvas")

        elif menu == "WEATHER (METAR/ATIS)":
            st.subheader("🌤️ AIRPORT WEATHER")
            icao_input = st.text_input("AIRPORT ICAO", "RJTT").upper().strip()
            if icao_input:
                res = requests.get(f"https://metar.vatsim.net/metar.php?id={icao_input}")
                if res.status_code == 200 and res.text.strip():
                    metar = res.text.strip()
                    st.markdown(f"<div style='background:#111; padding:15px; border-radius:5px; font-family:monospace; color:{accent_color};'>{metar}</div>", unsafe_allow_html=True)
                    st.markdown(f'<div style="margin-top:10px;"><a href="https://atis.guru/{icao_input}" target="_blank" style="color:{accent_color};">Open ATIS.GURU</a></div>', unsafe_allow_html=True)

        elif menu == "LOG":
            st.subheader("PILOT FLIGHT LOG")
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r", encoding="utf-8") as f: logs = json.load(f)
            else: logs = []
            with st.form("flight_log_full_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                log_date = c1.date_input("DATE", datetime.now())
                log_reg = c2.text_input("REGISTRATION")
                log_from = c1.text_input("FROM")
                log_to = c2.text_input("TO")
                if st.form_submit_button("SAVE RECORD"):
                    new_entry = {"date": str(log_date), "reg": log_reg.upper(), "from": log_from.upper(), "to": log_to.upper(), "maint_status": "PENDING"}
                    logs.append(new_entry)
                    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(logs, f, indent=4)
                    st.success("SAVED")

        elif menu == "UNIT CONVERTER":
            st.subheader("⚖️ UNIT CONVERTER")
            kg = st.number_input("KG to LB", value=0)
            st.write(f"{kg * 2.20462:.1f} LB")

        elif menu == "X-WIND CALC":
            st.subheader("X-WIND CALCULATOR")
            r_hdg = st.number_input("Runway", 0, 360, 340)
            w_dir = st.number_input("Wind Dir", 0, 360, 20)
            w_spd = st.number_input("Speed (KT)", 0, 100, 15)
            diff = abs(r_hdg - w_dir)
            st.metric("Crosswind", f"{abs(w_spd * math.sin(math.radians(diff))):.1f} KT")

        elif menu == "VATSIM TRAFFIC":
            st.subheader("VATSIM ONLINE")
            icao = st.text_input("AIRPORT ICAO", "RJTT").upper().strip()
            v_res = requests.get("https://data.vatsim.net/v3/vatsim-data.json")
            if v_res.status_code == 200:
                v_data = v_res.json()
                pilots = [p for p in v_data.get("pilots", []) if (p.get("flight_plan") or {}).get("arrival") == icao]
                for p in pilots[:5]: st.info(f"{p['callsign']} ➔ {icao}")

    # --- CHECKLIST TAB ---
    with main_tab2:
        st.subheader("AIRCRAFT CHECKLIST")
        ac_type = st.selectbox("SELECT AIRCRAFT", list(cl_db.keys()))
        phase = st.radio("SELECT PHASE", list(cl_db[ac_type].keys()), horizontal=True)
        st.markdown(f"### {ac_type} - {phase}")
        for item in cl_db[ac_type][phase]:
            st.checkbox(item, key=f"main_cl_{ac_type}_{phase}_{item}")

    # --- MAINTENANCE TAB ---
    with main_tab3:
        st.subheader("MAINTENANCE LOG")
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f: all_logs = json.load(f)
            for idx, entry in enumerate(reversed(all_logs)):
                with st.expander(f"{entry['date']} | {entry['reg']} - {entry.get('maint_status')}"):
                    if entry.get("maint_status") == "PENDING":
                        if st.button(f"APPROVE RELEASE (IDX:{idx})", key=f"maint_{idx}"):
                            all_logs[len(all_logs)-1-idx]["maint_status"] = "RELEASED"
                            with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(all_logs, f, indent=4)
                            st.rerun()

    if st.session_state['sw_running'] or st.session_state['timer_end']:
        time.sleep(1); st.rerun()
