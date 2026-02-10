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
    accent_color = "#3a86ff"  # Boeing Blue
    bg_color = "#1a2530"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg_color}; color: #FFFFFF; }}
        h1, h2, h3, p, label, .stMarkdown {{ color: #FFFFFF !important; }}
        .stTextInput>div>div>input {{ background-color: #FFFFFF !important; color: #000000 !important; border-radius: 4px !important; }}
        .stButton>button {{ background-color: #2c3e50 !important; color: #FFFFFF !important; border: 2px solid {accent_color} !important; border-radius: 4px !important; font-weight: bold; width: 100%; }}
        [data-testid="stSidebar"] {{ background-color: #121212; border-right: 1px solid #282828; min-width: 350px !important; }}
        .stTabs [data-baseweb="tab-list"] {{ position: static !important; background-color: transparent !important; border-bottom: 1px solid {accent_color}; }}
        div[role="radiogroup"] > label {{
            background-color: #16202a !important; border: 1px solid #455a64 !important;
            padding: 12px 20px !important; border-radius: 4px !important; margin-bottom: 6px !important;
            width: 100% !important; transition: all 0.2s ease !important; cursor: pointer !important;
        }}
        div[role="radiogroup"] > label[data-checked="true"] {{
            background-color: #1c2a38 !important; border-left: 5px solid {accent_color} !important;
            color: {accent_color} !important; font-weight: bold !important;
        }}
        </style>
        """, unsafe_allow_html=True)
else:
    accent_color = "#1DB954"  # Airbus/Standard Green
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

# --- 固定クイックリンクの設定 ---
default_links = [
    {"name": "ATIS GURU", "url": "https://atis.guru/"},
    {"name": "TRANSITION ALT LIST", "url": "https://docs.google.com/spreadsheets/d/1uTvrw-5uoGPuzGyB8lEkhyn7TO_HaZQ6WB-5N6nH-NM/edit?gid=1698518120#gid=1698518120"},
    {"name": "SIMBRIEF", "url": "https://www.simbrief.com/system/dispatch.php"},
    {"name": "NAVIGRAPH", "url": "https://charts.navigraph.com/"},
    {"name": "FAA NOTAM SEARCH", "url": "https://notams.aim.faa.gov/notamSearch/nsapp.html#/"}
]

if os.path.exists(LINK_FILE):
    with open(LINK_FILE, "r", encoding="utf-8") as f: quick_links = json.load(f)
    if not any("notams.aim.faa.gov" in l["url"] for l in quick_links):
        quick_links.append({"name": "FAA NOTAM SEARCH", "url": "https://notams.aim.faa.gov/notamSearch/nsapp.html#/"})
else:
    quick_links = default_links

# --- 3. Login Logic ---
if not st.session_state['authenticated']:
    st.title("EFBPro SYSTEM ACCESS")
    if st.text_input("ENTER ACCESS CODE", type="password") == "3910":
        st.session_state['authenticated'] = True
        st.rerun()
else:
    # --- Mode Switcher Button (右上) ---
    m_col1, m_col2 = st.columns([0.8, 0.2])
    with m_col2:
        if st.button(f"SW TO {'BOEING' if st.session_state['efb_mode'] == 'AIRBUS' else 'AIRBUS'} EFB"):
            st.session_state['efb_mode'] = "BOEING" if st.session_state['efb_mode'] == "AIRBUS" else "AIRBUS"
            st.rerun()

    with st.sidebar:
        st.title("EFBPro")
        st.markdown(f"**USER ID:** `{SB_USER}`")
        st.markdown("---")
        s_tab1, s_tab2 = st.tabs(["LINKS", "TOOLS"])
        
        with s_tab1:
            for link in quick_links:
                st.markdown(f'<a href="{link["url"]}" target="_blank" style="color:{accent_color}; text-decoration:none; font-weight:bold; display:block; margin:5px 0;">{link["name"]}</a>', unsafe_allow_html=True)
            
            st.markdown("---")
            with st.expander("ADD NEW LINK"):
                with st.form("add_link_form", clear_on_submit=True):
                    new_name = st.text_input("LINK NAME")
                    new_url = st.text_input("URL (https://...)")
                    if st.form_submit_button("ADD TO LIST") and new_name and new_url:
                        quick_links.append({"name": new_name, "url": new_url})
                        with open(LINK_FILE, "w", encoding="utf-8") as f: json.dump(quick_links, f, indent=4)
                        st.rerun()

        with s_tab2:
            menu = st.radio("SELECT TOOL", ["PILOT LOCATIONS", "TIMERS", "OFP", "T/D CALC", "TURN RADIUS", "PAD", "WEATHER (METAR/ATIS)", "LOG", "UNIT CONVERTER", "X-WIND CALC", "VATSIM TRAFFIC"])

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
                    else:
                        st.error("フライトプランが見つかりません。SimBriefで GENERATE OFP 済みですか？")
            
            if st.session_state.get('sb_json'):
                sb = st.session_state['sb_json']
                to_data = sb.get('takeoff', {})
                v1, vr, v2 = to_data.get('v1', '--'), to_data.get('vr', '--'), to_data.get('v2', '--')
                trim = to_data.get('trim', 'N/A')
                tow = sb.get('weights', {}).get('est_takeoff_weight', '0')

                st.markdown(f"""
                <div style="background: {bg_color if st.session_state['efb_mode'] == 'BOEING' else '#1a1a1a'}; padding: 20px; border-radius: 10px; border-left: 5px solid {accent_color}; margin-bottom: 20px;">
                    <p style="color: #888; margin: 0; font-size: 0.9em;">TAKEOFF PERFORMANCE</p>
                    <div style="display: flex; justify-content: space-around; text-align: center; padding: 15px 0;">
                        <div><div style="color:#888; font-size:0.8em;">V1</div><h1 style="margin:0;">{v1}</h1></div>
                        <div><div style="color:#888; font-size:0.8em;">VR</div><h1 style="margin:0;">{vr}</h1></div>
                        <div><div style="color:#888; font-size:0.8em;">V2</div><h1 style="margin:0;">{v2}</h1></div>
                    </div>
                    <div style="text-align: center; border-top: 1px solid #333; pt-10px; margin-top: 10px;">
                        <span style="color:#888;">STAB TRIM:</span> <span style="color:{accent_color}; font-weight:bold; font-size:1.2em;">{trim}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("### Flight Information")
                info_col1, info_col2, info_col3, info_col4, info_col5 = st.columns(5)
                with info_col1: st.metric("CALLSIGN", sb.get('atc', {}).get('callsign', "N/A"))
                with info_col2: st.metric("TOW", f"{int(tow)/1000:.1f} T")
                with info_col3: st.metric("TYPE", sb.get('aircraft', {}).get('icaocode', "N/A"))
                with info_col4: st.metric("ORIGIN", sb.get('origin', {}).get('icao_code', "N/A"))
                with info_col5: st.metric("DEST", sb.get('destination', {}).get('icao_code', "N/A"))
                st.info(f"**ROUTE:** {sb.get('general', {}).get('route', 'N/A')}")

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
            st.metric("Turn Radius (NM)", f"{(radius / 6076.12):.2f} NM")

        elif menu == "PAD":
            st.subheader("FLIGHT MEMO / SCRATCH PAD")
            c1, c2, c3 = st.columns([1, 1, 2])
            draw_mode = c1.selectbox("TOOL", ["freedraw", "transform"], format_func=lambda x: "Pencil" if x=="freedraw" else "Selection/Eraser")
            stroke_color = c2.selectbox("COLOR", ["#FFFFFF", "#FF4B4B", "#121212"], format_func=lambda x: "WHITE" if x=="#FFFFFF" else "RED" if x=="#FF4B4B" else "ERASER")
            stroke_width = c3.slider("WIDTH", 1, 20, 3)
            st_canvas(fill_color="rgba(255, 165, 0, 0.3)", stroke_width=stroke_width, stroke_color=stroke_color, background_color="#121212", height=400, drawing_mode=draw_mode, key="canvas")
            if st.button("CLEAR PAD"): st.rerun()

        elif menu == "WEATHER (METAR/ATIS)":
            st.subheader("🌤️ AIRPORT WEATHER")
            icao_input = st.text_input("AIRPORT ICAO", "RJTT").upper().strip()
            if icao_input:
                res = requests.get(f"https://metar.vatsim.net/metar.php?id={icao_input}")
                if res.status_code == 200 and res.text.strip():
                    metar = res.text.strip()
                    w = re.search(r"(\d{3}|VRB)(\d{2,3})KT", metar)
                    v = re.search(r"\b(\d{4})\b", metar)
                    t_d = re.search(r"(\d{2})/(M?\d{2})", metar)
                    q = re.search(r"Q(\d{4})", metar)
                    a = re.search(r"A(\d{4})", metar)
                    
                    humidity = "N/A"
                    if t_d:
                        temp = int(t_d.group(1))
                        dew = int(t_d.group(2).replace('M', '-'))
                        rh = 100 - 5 * (temp - dew)
                        humidity = f"{max(0, min(100, rh))}%"

                    st.markdown(f"""
                    <div style="background: #12151a; padding: 25px; border-radius: 5px; font-family: sans-serif;">
                        <div style="color: #6da5ff; font-weight: bold; margin-bottom: 15px; font-family: monospace;">{metar}</div>
                        <div style="border-bottom: 1px solid #2d343e; padding: 8px 0; display: flex; justify-content: space-between;">
                            <span style="color: #8892a0;">Wind</span> <span style="color: #fff;">{w.group(1)+'° at '+w.group(2)+' KT' if w else 'N/A'}</span>
                        </div>
                        <div style="border-bottom: 1px solid #2d343e; padding: 8px 0; display: flex; justify-content: space-between;">
                            <span style="color: #8892a0;">Temperature</span> <span style="color: #fff;">{t_d.group(1) if t_d else '--'}° C</span>
                        </div>
                        <div style="border-bottom: 1px solid #2d343e; padding: 8px 0; display: flex; justify-content: space-between;">
                            <span style="color: #8892a0;">Dew point</span> <span style="color: #fff;">{t_d.group(2).replace('M', '-') if t_d else '--'}° C</span>
                        </div>
                        <div style="border-bottom: 1px solid #2d343e; padding: 8px 0; display: flex; justify-content: space-between;">
                            <span style="color: #8892a0;">Humidity</span> <span style="color: #fff;">{humidity}</span>
                        </div>
                        <div style="border-bottom: 1px solid #2d343e; padding: 8px 0; display: flex; justify-content: space-between;">
                            <span style="color: #8892a0;">Altimeter</span> <span style="color: #fff;">{q.group(1) if q else '----'} hPa ({a.group(1)[:2]+'.'+a.group(1)[2:] if a else '--.--'} inHg)</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f'<div style="margin-top:10px;"><a href="https://atis.guru/{icao_input}" target="_blank" style="color:{accent_color}; text-decoration:none;">Open ATIS.GURU</a></div>', unsafe_allow_html=True)

        elif menu == "LOG":
            st.subheader("PILOT FLIGHT LOG & MAINTENANCE RECORD")
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r", encoding="utf-8") as f: logs = json.load(f)
            else: logs = []
            sb_data = st.session_state.get('sb_json') or {}
            ac_info = sb_data.get('aircraft', {})
            with st.form("flight_log_full_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                log_date = c1.date_input("月 日～年", datetime.now())
                log_ac_type = c2.text_input("航空機型式", value=ac_info.get('icaocode', ""))
                log_reg = c3.text_input("登録記号", value=ac_info.get('reg', ""))
                c4, c5, c6, c7 = st.columns(4)
                log_from = c4.text_input("FROM", value=sb_data.get('origin', {}).get('icao_code', ""))
                log_to = c5.text_input("TO", value=sb_data.get('destination', {}).get('icao_code', ""))
                log_dtime = c6.text_input("(D)TIME (UTC)")
                log_atime = c7.text_input("(A)TIME (UTC)")
                c8, c9, c10 = st.columns(3)
                log_content = c8.text_input("飛行内容", value="定期便")
                log_toldg = c9.text_input("T/O LDG (回数)")
                log_total_time = c10.text_input("飛行時間")
                c11, c12 = st.columns(2)
                log_sign = c11.text_input("証明 (PILOT SIGN)")
                log_extra = st.text_area("補足")
                if st.form_submit_button("SAVE RECORD"):
                    new_entry = {"date": str(log_date), "ac_type": log_ac_type.upper(), "reg": log_reg.upper(), "from": log_from.upper(), "to": log_to.upper(), "d_time": log_dtime, "a_time": log_atime, "content": log_content, "toldg": log_toldg, "total_time": log_total_time, "sign": log_sign, "extra": log_extra, "maint_status": "PENDING", "ts": time.time()}
                    logs.append(new_entry)
                    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(logs, f, indent=4)
                    st.success("運行記録が保存されました！")
                    st.rerun()

        elif menu == "UNIT CONVERTER":
            st.subheader("⚖️ UNIT CONVERTER")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Weight (KG ⟷ LB)**")
                kg = st.number_input("Kilograms", value=0)
                st.code(f"{kg * 2.20462:.1f} LB")
                lb = st.number_input("Pounds", value=0)
                st.code(f"{lb / 2.20462:.1f} KG")
            with col2:
                st.write("**Volume (L ⟷ KG JetA1)**")
                liter = st.number_input("Liters", value=0)
                st.code(f"{liter * 0.8:.1f} KG")
                st.write("**Altitude (FT ⟷ M)**")
                feet = st.number_input("Feet", value=0)
                st.code(f"{feet * 0.3048:.1f} M")

        elif menu == "X-WIND CALC":
            st.subheader("X-WIND CALCULATOR")
            r_hdg = st.number_input("Runway", 0, 360, 340)
            w_dir = st.number_input("Wind Dir", 0, 360, 20)
            w_spd = st.number_input("Speed (KT)", 0, 100, 15)
            diff = abs(r_hdg - w_dir)
            st.metric("Crosswind", f"{abs(w_spd * math.sin(math.radians(diff))):.1f} KT")

        elif menu == "VATSIM TRAFFIC":
            st.subheader("VATSIM ONLINE TRAFFIC")
            icao = st.text_input("AIRPORT ICAO", "RJTT").upper().strip()
            v_res = requests.get("https://data.vatsim.net/v3/vatsim-data.json")
            if v_res.status_code == 200:
                v_data = v_res.json()
                st.write("---")
                st.write("**VATJPN ONLINE CONTROLLERS**")
                conts = [c for c in v_data.get("controllers", []) if c.get("callsign", "").upper().startswith(("RJ", "RO"))]
                if conts:
                    for c in conts: st.success(f"**{c['callsign']}** ({c['name']}) - {c.get('frequency', 'N/A')}")
                else: st.write("📡 No controllers online in Japan region.")
                
                st.write(f"**TRAFFIC AT {icao}**")
                pilots = []
                for p in v_data.get("pilots", []):
                    fplan = p.get("flight_plan")
                    dep = (p.get("departure") or (fplan.get("departure") if fplan else "") or "").upper()
                    arr = (p.get("arrival") or (fplan.get("arrival") if fplan else "") or "").upper()
                    if dep == icao or arr == icao: pilots.append(p)

                if pilots:
                    for p in pilots:
                        fplan = p.get("flight_plan")
                        st.info(f"**{p['callsign']}** | {(fplan.get('departure') if fplan else '???')} ➔ {(fplan.get('arrival') if fplan else '???')} | ALT: {p.get('altitude', 0)}ft")
                else: st.write(f"🛬 No traffic reported for {icao}.")

    # --- CHECKLIST TAB ---
    with main_tab2:
        st.subheader("AIRCRAFT CHECKLIST")
        ac_type = st.selectbox("SELECT AIRCRAFT", list(cl_db.keys()))
        phase = st.radio("SELECT PHASE", list(cl_db[ac_type].keys()), horizontal=True)
        st.markdown("---")
        st.markdown(f"### {ac_type} - {phase}")
        for item in cl_db[ac_type][phase]:
            st.checkbox(item, key=f"main_cl_{ac_type}_{phase}_{item}")
        if st.button("RESET CURRENT PHASE"): st.rerun()

    # --- MAINTENANCE TAB ---
    with main_tab3:
        st.subheader("整備士確認 (MAINTENANCE LOG)")
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f: all_logs = json.load(f)
        else: all_logs = []
        if not all_logs: st.info("未処理の記録はありません。")
        else:
            for idx, entry in enumerate(reversed(all_logs)):
                status_color = accent_color if entry.get("maint_status") == "RELEASED" else "#FF4B4B"
                with st.expander(f"{entry['date']} | {entry['reg']} ({entry['from']} -> {entry['to']}) - {entry.get('maint_status', 'PENDING')}"):
                    st.markdown(f"**フライト詳細:**\n* **飛行内容:** {entry['content']} | **飛行時間:** {entry['total_time']} | **T/O LDG:** {entry['toldg']}\n* **補足:** {entry['extra']} | **署名:** {entry['sign']}")
                    st.markdown(f"<p style='color:{status_color}; font-weight:bold;'>STATUS: {entry.get('maint_status', 'PENDING')}</p>", unsafe_allow_html=True)
                    if entry.get("maint_status") == "PENDING":
                        if st.button(f"機体リリースを承認 (IDX:{idx})", key=f"maint_btn_{idx}"):
                            actual_idx = len(all_logs) - 1 - idx
                            all_logs[actual_idx]["maint_status"] = "RELEASED"
                            with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(all_logs, f, indent=4)
                            st.balloons(); st.rerun()

    if st.session_state['sw_running'] or st.session_state['timer_end']:
        time.sleep(1); st.rerun()
