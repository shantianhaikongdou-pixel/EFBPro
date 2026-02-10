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

# --- Checklist Database ---
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
        "ELECTRICAL POWERUP": ["SERVICE INTERPHONE - OFF", "BACKUP WINDOW HEAT - ON", "PRIMARY WINDOW HEAT - ON", "ENGINE PRIMARY PUMP L&R - ON", "C1 & C2 ELEC PUMP - OFF", "L & R DEMAND PUMP - OFF", "SEAT BELT SIG SIGNS - ON", "APU FIRE PANEL - SET", "CARGO FIRE ARM - NORM", "ENGINE EEC MODE - NORM", "FUEL JETTISON - OFF", "WING/ENGINE ANTI-ICE - AUTO"],
        "BEFORE START": ["FLIGHT DECK DOOR - CLOSED/LOCKED", "PASSENGER SIGNS - ON", "MCP - SET", "FMS - COMPLETED", "BEACON - ON"],
        "AFTER START/TAXI": ["FLAPS - SET", "AUTOBRAKE - RTO", "FLIGHT CONTROLS - CHECKED"],
        "CLIMB/CRUISE": ["LANDING GEAR - UP", "FLAPS - UP", "ALTIMETERS - STD", "ANTI-ICE - AS REQ"],
        "DESCENT": ["PRESSURIZATION (LDG ALT) - SET", "RECALL - CHECKED", "AUTOBRAKE - SET", "LANDING DATA (VREF) - VERIFY", "APPROACH BRIEFING - COMPLETE"],
        "APPROACH/LANDING": ["ALTIMETER - RESET TO LOCAL", "SPEED - 250 KIAS (BELOW 10k)", "LANDING LIGHTS - ON", "SEAT BELTS - ON"],
        "SHUTDOWN/POWER DOWN": ["PARKING BRAKE - SET", "APU - VERIFY RUNNING", "FUEL CONTROL SWITCHES - CUTOFF", "SEAT BELT SIGNS - OFF", "FUEL PUMPS - OFF", "BEACON LIGHT - OFF", "IRS SELECTORS - OFF", "FD DOOR POWER - OFF"]
    },
    # ... A320, B777, B767, A330, HondaJet (データ保持)
}

# --- 1. Page Configuration ---
st.set_page_config(page_title="EFBPro | Boeing Mode", layout="wide", initial_sidebar_state="collapsed")

# --- 2. Styling (Boeing Hardware Look) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    /* Hide Sidebar in Boeing Mode */
    [data-testid="stSidebar"] { display: none; }
    
    /* Boeing Button Style */
    .stButton>button {
        background-color: #3e444c !important;
        color: #d1d2d3 !important;
        border: 2px solid #555 !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        height: 50px !important;
        text-transform: uppercase;
    }
    .stButton>button:hover { border-color: #3a86ff !important; color: #fff !important; }
    
    /* Header Style */
    .efb-header {
        text-align: center;
        border-bottom: 2px solid #333;
        padding-bottom: 10px;
        margin-bottom: 20px;
        color: #aaa;
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. Persistence & State ---
DB_FILE, LINK_FILE, POS_FILE = "pilot_logbook.json", "quick_links.json", "pilot_positions.json"
SB_USER = "906331"

if 'authenticated' not in st.session_state: st.session_state['authenticated'] = False
if 'menu' not in st.session_state: st.session_state['menu'] = "MAIN MENU"
if 'sb_json' not in st.session_state: st.session_state['sb_json'] = None
if 'sw_running' not in st.session_state: st.session_state['sw_running'] = False
if 'sw_start_time' not in st.session_state: st.session_state['sw_start_time'] = 0
if 'timer_end' not in st.session_state: st.session_state['timer_end'] = None

# --- Data Load (Existing logic) ---
if os.path.exists(POS_FILE):
    with open(POS_FILE, "r", encoding="utf-8") as f: p_pos = json.load(f)
else:
    p_pos = {"ANA": "RJTT", "JAL": "RJTT", "HDJT": "RJTT", "Delta": "KATL", "Lufthansa": "EDDF"}

# --- 4. Logic & UI ---
if not st.session_state['authenticated']:
    st.title("EFBPro SYSTEM ACCESS")
    if st.text_input("ENTER ACCESS CODE", type="password") == "3910":
        st.session_state['authenticated'] = True
        st.rerun()
else:
    # --- Top Nav ---
    st.markdown(f'<div class="efb-header">--- {st.session_state["menu"]} ---</div>', unsafe_allow_html=True)
    
    # 2カラム配置 (左メニュー | コンテンツ | 右メニュー)
    l_col, mid_col, r_col = st.columns([1, 4, 1])

    with l_col:
        if st.button("OFP"): st.session_state['menu'] = "OFP"
        if st.button("CHECKLIST"): st.session_state['menu'] = "CHECKLIST"
        if st.button("WEATHER"): st.session_state['menu'] = "WEATHER"
        if st.button("TIMERS"): st.session_state['menu'] = "TIMERS"
        if st.button("PAD"): st.session_state['menu'] = "PAD"
        if st.button("VATSIM"): st.session_state['menu'] = "VATSIM"

    with r_col:
        if st.button("LOCATIONS"): st.session_state['menu'] = "LOCATIONS"
        if st.button("LOG"): st.session_state['menu'] = "LOG"
        if st.button("MAINT"): st.session_state['menu'] = "MAINTENANCE"
        if st.button("T/D CALC"): st.session_state['menu'] = "T/D CALC"
        if st.button("X-WIND"): st.session_state['menu'] = "X-WIND"
        if st.button("MENU"): st.session_state['menu'] = "MAIN MENU"

    with mid_col:
        menu = st.session_state['menu']
        
        if menu == "MAIN MENU":
            st.write("SELECT A FUNCTION FROM THE SIDE KEYS")

        elif menu == "OFP":
            if st.button("FETCH SIMBRIEF"):
                res = requests.get(f"https://www.simbrief.com/api/xml.fetcher.php?userid={SB_USER}&json=1")
                if res.status_code == 200:
                    st.session_state['sb_json'] = res.json()
                    st.rerun()
            if st.session_state.get('sb_json'):
                sb = st.session_state['sb_json']
                st.markdown(f"**CALLSIGN:** {sb.get('atc',{}).get('callsign')}")
                st.info(f"ROUTE: {sb.get('general',{}).get('route')}")
                c1, c2, c3 = st.columns(3)
                c1.metric("V1", sb.get('takeoff',{}).get('v1','--'))
                c2.metric("VR", sb.get('takeoff',{}).get('vr','--'))
                c3.metric("V2", sb.get('takeoff',{}).get('v2','--'))

        elif menu == "CHECKLIST":
            ac_type = st.selectbox("AIRCRAFT", list(cl_db.keys()))
            phase = st.radio("PHASE", list(cl_db[ac_type].keys()), horizontal=True)
            for item in cl_db[ac_type][phase]:
                st.checkbox(item, key=f"cl_{ac_type}_{phase}_{item}")

        elif menu == "LOCATIONS":
            for airline, icao in p_pos.items():
                new_icao = st.text_input(airline, icao).upper()
                if new_icao != icao:
                    p_pos[airline] = new_icao
                    with open(POS_FILE, "w", encoding="utf-8") as f: json.dump(p_pos, f)

        elif menu == "WEATHER":
            icao = st.text_input("ICAO", "RJTT").upper()
            res = requests.get(f"https://metar.vatsim.net/metar.php?id={icao}")
            if res.status_code == 200: st.code(res.text, language="text")

        elif menu == "LOG":
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r", encoding="utf-8") as f: logs = json.load(f)
            else: logs = []
            with st.form("log_form"):
                d = st.date_input("DATE")
                r = st.text_input("REG")
                f, t = st.columns(2)
                frm = f.text_input("FROM")
                to = t.text_input("TO")
                if st.form_submit_button("SAVE"):
                    logs.append({"date": str(d), "reg": r.upper(), "from": frm.upper(), "to": to.upper(), "maint_status": "PENDING"})
                    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(logs, f, indent=4)
                    st.success("SAVED")

        elif menu == "MAINTENANCE":
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r", encoding="utf-8") as f: all_logs = json.load(f)
                for idx, entry in enumerate(reversed(all_logs)):
                    if entry['maint_status'] == "PENDING" and st.button(f"RELEASE: {entry['reg']} ({entry['date']})"):
                        all_logs[len(all_logs)-1-idx]["maint_status"] = "RELEASED"
                        with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(all_logs, f, indent=4)
                        st.rerun()

        elif menu == "TIMERS":
            c1, c2 = st.columns(2)
            if c1.button("START SW"):
                st.session_state['sw_start_time'] = time.time()
                st.session_state['sw_running'] = True
            if st.session_state['sw_running']:
                st.header(time.strftime('%H:%M:%S', time.gmtime(time.time() - st.session_state['sw_start_time'])))
            t_min = c2.number_input("MIN", 1, 180, 15)
            if c2.button("SET TIMER"): st.session_state['timer_end'] = time.time() + (t_min * 60)

        elif menu == "PAD":
            st_canvas(stroke_width=3, stroke_color="#fff", background_color="#121212", height=400, key="canvas")

        elif menu == "T/D CALC":
            ca = st.number_input("Current Alt", 0, 45000, 35000)
            ta = st.number_input("Target Alt", 0, 45000, 3000)
            st.metric("Dist", f"{((ca - ta) / 1000) * 3:.1f} NM")

        elif menu == "X-WIND":
            r_hdg = st.number_input("Runway", 0, 360, 340)
            w_dir = st.number_input("Wind Dir", 0, 360, 20)
            w_spd = st.number_input("Speed", 0, 100, 15)
            xw = abs(w_spd * math.sin(math.radians(abs(r_hdg - w_dir))))
            st.metric("X-Wind", f"{xw:.1f} KT")

        elif menu == "VATSIM":
            v_res = requests.get("https://data.vatsim.net/v3/vatsim-data.json")
            if v_res.status_code == 200:
                pilots = v_res.json().get("pilots", [])[:10]
                for p in pilots: st.text(f"{p['callsign']} | {p.get('flight_plan',{}).get('arrival','---')}")

    if st.session_state['sw_running']:
        time.sleep(1)
        st.rerun()
        st.rerun()
