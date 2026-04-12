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

# --- Checklist Database (みくとの全機体リスト) ---
cl_db = {
    "A350": {"COCKPIT PREP": ["PARKING BRAKE - SET", "ALL BATTERY SWITCH - ON", "EXTERNAL POWER - PUSH", "ADIRS (1, 2, 3) - NAV", "CREW SUPPLY - ON", "PACKS - AUTO", "NAV LIGHTS - ON", "LOGO LIGHTS - ON", "APU - MASTER-START", "NO SMOKING - AUTO", "NO MOBILE - AUTO", "EMERGENCY LIGHTS - ARMED", "FLIGHT DIRECTORS - ON", "ALTIMETERS - SET", "MCDU - SETUP", "FLT CTL PAGE - CHECK"], "BEFORE START": ["WINDOWS/DOORS - CLOSED", "BEACON - ON", "THRUST LEVERS - IDLE", "FUEL PUMPS - ON", "TRANSPONDER - AS REQ"], "AFTER START": ["ENGINE MODE SELECTOR - NORM", "PITCH TRIM - SET", "AUTOBRAKE - MAX", "FLAPS - SET", "GND SPOILERS - ARMED", "APU - OFF", "FLIGHT CONTROLS - CHECKED", "RUDDER TRIM - ZERO", "ANTI-ICE - AS REQ"], "TAXI/TAKEOFF": ["GROUND EQUIPMENT - CLEAR", "NOSEWHEEL LIGHTS - TAXI", "BRAKES - CHECK", "AUTO THRUST - BLUE", "TCAS - TA/RA", "PACKS - OFF/ON"], "CRUISE": ["ALTIMETERS - STD", "ANTI-ICE - AS REQ", "ECAM MEMO - CHECKED"], "DESCENT/APPROACH": ["CABIN CREW - ADVISED", "ND TERRAIN - AS REQ", "APPROACH BUTTON - ARM", "APPR PHASE (MCDU) - ACTIVATE", "LANDING GEAR - DOWN"], "LANDING": ["GND SPOILERS - ARM", "ENG MODE SELECTOR - AS REQ", "AUTOBRAKE - AS REQ", "FLAPS - SET LDG", "GO AROUND ALTITUDE - SET", "ECAM MEMO - LDG NO BLUE"], "SHUTDOWN/SECURE": ["PARKING BRAKE - SET", "APU - START", "ENG 1 & 2 MASTER - OFF", "BEACON LIGHTS - OFF", "FLIGHT DIRECTORS - OFF", "PASSENGER SIGNS - OFF", "SLIDES - DISARM", "FUEL PUMPS - OFF", "DOORS - OPEN", "ADIRS - OFF", "EMERGENCY LIGHTS - OFF", "NAV/LOGO LIGHTS - OFF", "EXTERNAL POWER - OFF", "BATTERY - OFF"]},
    "B787": {"ELECTRICAL POWERUP": ["SERVICE INTERPHONE - OFF", "BACKUP WINDOW HEAT - ON", "PRIMARY WINDOW HEAT - ON", "ENGINE PRIMARY PUMP L&R - ON", "C1 & C2 ELEC PUMP - OFF", "L & R DEMAND PUMP - OFF", "SEAT BELT SIGNS - ON", "APU FIRE PANEL - SET", "CARGO FIRE ARM - NORM", "ENGINE EEC MODE - NORM", "FUEL JETTISON - OFF", "WING/ENGINE ANTI-ICE - AUTO"], "BEFORE START": ["FLIGHT DECK DOOR - CLOSED/LOCKED", "PASSENGER SIGNS - ON", "MCP - SET", "FMS - COMPLETED", "BEACON - ON"], "AFTER START/TAXI": ["FLAPS - SET", "AUTOBRAKE - RTO", "FLIGHT CONTROLS - CHECKED"], "CLIMB/CRUISE": ["LANDING GEAR - UP", "FLAPS - UP", "ALTIMETERS - STD", "ANTI-ICE - AS REQ"], "DESCENT": ["PRESSURIZATION (LDG ALT) - SET", "RECALL - CHECKED", "AUTOBRAKE - SET", "LANDING DATA (VREF) - VERIFY", "APPROACH BRIEFING - COMPLETE"], "APPROACH/LANDING": ["ALTIMETER - RESET TO LOCAL", "SPEED - 250 KIAS (BELOW 10k)", "LANDING LIGHTS - ON", "SEAT BELTS - ON"], "SHUTDOWN/POWER DOWN": ["PARKING BRAKE - SET", "APU - VERIFY RUNNING", "FUEL CONTROL SWITCHES - CUTOFF", "SEAT BELT SIGNS - OFF", "FUEL PUMPS - OFF", "BEACON LIGHT - OFF", "IRS SELECTORS - OFF", "FD DOOR POWER - OFF"]},
    "A320/321": {"COCKPIT PREP": ["GEAR PINS and COVERS - REMOVED", "FUEL QUANTITY - KG CHECK", "SIGNS - ON/AUTO", "ADIRS - NAV", "BARO REF - SET (BOTH)"], "BEFORE START": ["PARKING BRAKE - SET", "T.O SPEEDS & THRUST - BOTH SET", "WINDOWS/DOORS - CLOSED", "BEACON - ON"], "AFTER START": ["APU - OFF", "Y ELEC PUMP - OFF", "ANTI ICE - AS REQ", "PITCH TRIM - SET", "RUDDER TRIM - ZERO"], "APPROACH": ["BARO REF - SET", "SEAT BELTS - ON", "MINIMUM - SET", "ENG MODE SEL - AS REQ"], "LANDING": ["G/A ALTITUDE - SET", "CABIN CREW - ADVISED", "ECAM MEMO - LDG NO BLUE", "LDG GEAR - DOWN", "SPLRS - ARM", "FLAPS - SET"], "PARKING/SECURE": ["PARKING BRAKE - SET", "ENGINES - OFF", "FUEL PUMPS - OFF", "ADIRS - OFF", "EXT PWR - AS REQ"]},
    "B777": {"PREFLIGHT": ["ADIRU Switch - ON", "Emergency Exit Lights - ARMED", "Hydraulic Panel - SET", "Electrical Panel - SET", "Packs - ON", "FMC - SETUP"], "BEFORE START": ["Flight Deck Door - CLOSED", "Passenger Signs - ON", "MCP - SET", "Takeoff Speeds - SET", "Beacon - ON"], "AFTER START/TAXI": ["Anti-ice - AS REQ", "Recall - CHECKED", "Autobrake - RTO", "Flaps - SET", "Flight Controls - CHECKED"], "BEFORE TAKEOFF": ["Transponder - TA/RA", "Strobe Lights - ON"], "CRUISE": ["Altimeters - STD", "FMC/Fuel - CHECKED"], "DESCENT/APPROACH": ["Altimeters - QNH SET", "Landing Data - SET", "Autobrake - SET"], "SHUTDOWN": ["Hydraulic Panel - SET", "Fuel Pumps - OFF", "Flaps - UP", "Parking Brake - AS REQ", "Fuel Control Switches - CUTOFF", "Weather Radar - OFF"], "SECURING": ["ADIRU Switch - OFF", "Emergency Exit Lights - OFF", "Packs Switches - OFF", "APU - OFF"]},
    "B767": {"PREFLIGHT": ["Oxygen - TESTED", "IRS - OFF TO NAV", "HYDRAULIC PANEL - SET", "WINDOW HEAT - ON", "THROTTLES - IDLE", "GEAR PIN - REMOVED", "PARKING BRAKE - SET"], "BEFORE START": ["FUEL - KGS/PUMPS ON", "WINDOWS - CLOSED/LOCKED", "PASSENGER SIGNS - ON", "DOORS - CLOSED & ARMED"], "AFTER START": ["PROBE HEAT - ON", "ANTI-ICE - AS REQ", "ISOLATION VALVE - OFF", "FUEL CTRL - RUN & LOCKED"], "BEFORE TAXI": ["RECALL - CHECKED", "FLT CTRLS - CHECKED", "FLAPS - SET", "AUTOBRAKE - RTO"], "AFTER TAKEOFF": ["LANDING GEAR - UP & OFF", "FLAPS - UP", "ALTIMETERS - SET STD"], "DESCENT/APPROACH": ["LDG ALT - SET", "PASSANGER SIGNS - ON", "RECALL - CHECKED", "AUTOBRAKE - SET", "VREF/MINIMUMS - SET", "ALTIMETERS - QNH SET"], "LANDING": ["CABIN - SECURED", "SPEEDBRAKE - ARMED", "LANDING GEAR - DOWN", "FLAPS - SET"], "AFTER LANDING": ["ANTI-ICE - AS REQ", "APU - STARTED", "AUTOBRAKE - OFF", "SPEEDBRAKE - DOWN", "FLAPS - UP", "WEATHER RADAR - OFF"]},
    "A330": {"COCKPIT PREP": ["GEAR PINS & COVERS - REMOVED", "FUEL QUANTITY - CHECK", "SEAT BELTS - ON", "ADIRS - NAV", "BARO REF - BOTH SET"], "BEFORE START": ["T.O SPEEDS & THRUST - BOTH SET", "WINDOWS - CLOSED", "BEACON - ON", "PARKING BRAKE - SET"], "AFTER START": ["ANTI ICE - AS REQ", "ECAM STATUS - CHECKED", "PITCH TRIM - SET", "RUDDER TRIM - CHECKED"], "APPROACH": ["BARO REF - BOTH SET", "SEAT BELTS - ON", "MINIMUM - SET", "AUTO BRAKE - SET", "ENG START SEL - AS REQ"], "LANDING": ["ECAM MEMO - LDG NO BLUE", "GEAR - DOWN", "FLAPS - SET"], "AFTER LANDING": ["RADAR & PRED W/S - OFF", "SPOILERS - DISARM", "FLAPS - RETRACT", "APU - START"], "PARKING": ["PARKING BRAKE/CHOCKS - SET", "ENGINES - OFF", "FUEL PUMPS - OFF"]},
    "HondaJet": {"CDU SETUP": ["Database Status - CONNECT", "Avionics Settings - AS DESIRED", "Flight Plan - ENTER/VERIFY"], "BEFORE START": ["ATC Clearance - OBTAIN", "Transponder - SQUAWK SET", "Alt Select - SET CLEARED ALT", "Parking Brake - SET", "Battery - ON", "External Power - AS REQ"], "ENGINE START": ["Doors - CLOSED", "Parking Brake - SET", "CAS Messages - REVIEW", "Elec Volts - MIN 23.5V", "Engine Start Button - PUSH"], "AFTER START/TAXI": ["External Power - DISCONNECT", "Lights - AS REQ", "Flaps - TAKE OFF", "Trim - SET (GREEN)"], "CRUISE": ["Altimeter - STD", "Ice Protection - AS REQ", "Fuel - MONITOR"], "LANDING": ["Landing Gear - DOWN & 3 GREEN", "Flaps - LDG", "Yaw Damper - OFF @50ft", "Throttles - IDLE @Threshold"], "SHUTDOWN": ["Parking Brake - SET", "Engines - OFF", "Electrical - OFF"]}
}

st.set_page_config(page_title="EFBPro | Flight Portal", layout="wide")

# --- Session State Initializer ---
if 'efb_mode' not in st.session_state: st.session_state['efb_mode'] = "AIRBUS"
if 'authenticated' not in st.session_state: st.session_state['authenticated'] = False
if 'sb_json' not in st.session_state: st.session_state['sb_json'] = None
if 'sw_running' not in st.session_state: st.session_state['sw_running'] = False
if 'sw_start_time' not in st.session_state: st.session_state['sw_start_time'] = 0

# --- Dynamic Styling ---
if st.session_state['efb_mode'] == "BOEING":
    bg_color, accent_color, text_color = "#1a2530", "#3a86ff", "#e0e0e0"
    css_extra = f"""
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .stButton>button {{ background-color: #2c3e50 !important; color: white !important; border: 2px solid {accent_color} !important; border-radius: 4px !important; }}
    div[role="radiogroup"] > label {{ background-color: #16202a !important; border: 1px solid #455a64 !important; color: #cfd8dc !important; padding: 12px 20px !important; border-radius: 4px !important; margin-bottom: 6px !important; width: 100% !important; }}
    div[role="radiogroup"] > label[data-checked="true"] {{ background-color: #1c2a38 !important; border-left: 5px solid {accent_color} !important; color: {accent_color} !important; }}
    .ams-header {{ background-color: #ffffff; color: #000; padding: 10px; border-radius: 4px 4px 0 0; font-weight: bold; display: flex; justify-content: space-between; }}
    .ams-table {{ width: 100%; background-color: #2c3e50; border-collapse: collapse; color: #fff; font-size: 0.9em; }}
    .ams-table th {{ background-color: #34495e; color: #8892a0; text-align: left; padding: 10px; font-weight: normal; border-bottom: 1px solid #444; }}
    .ams-table td {{ padding: 10px; border-bottom: 1px solid #444; }}
    .ams-green {{ color: #2ecc71; font-weight: bold; }}
    .ams-input {{ background-color: #fff; color: #000; padding: 2px 5px; border-radius: 2px; }}
    """
else:
    bg_color, accent_color, text_color = "#000000", "#1DB954", "#FFFFFF"
    css_extra = f"""
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .stButton>button {{ background-color: {accent_color} !important; color: #FFFFFF !important; border-radius: 4px !important; border: none; width: 100%; }}
    div[role="radiogroup"] > label {{ background-color: #1a1a1a !important; border: 1px solid #333 !important; padding: 12px 20px !important; border-radius: 4px !important; margin-bottom: 6px !important; width: 100% !important; }}
    div[role="radiogroup"] > label[data-checked="true"] {{ background-color: #252525 !important; border-left: 5px solid {accent_color} !important; color: {accent_color} !important; }}
    """

st.markdown(f"<style>{css_extra} h1, h2, h3, p, label, .stMarkdown {{ color: {text_color} !important; }} .stTextInput>div>div>input {{ background-color: #FFFFFF !important; color: #000000 !important; border-radius: 4px !important; }} [data-testid='stSidebar'] {{ background-color: #121212; border-right: 1px solid #282828; min-width: 350px !important; }} div[role='radiogroup'] > label > div:first-child {{ display: none !important; }}</style>", unsafe_allow_html=True)

# --- Files Management ---
DB_FILE, LINK_FILE, POS_FILE = "pilot_logbook.json", "quick_links.json", "pilot_positions.json"
SB_USER = "906331" 

if os.path.exists(POS_FILE):
    with open(POS_FILE, "r", encoding="utf-8") as f: p_pos = json.load(f)
else:
    p_pos = {"ANA": "RJTT", "JAL": "RJTT", "HDJT": "RJTT", "Delta": "KATL", "Lufthansa": "EDDF"}

if os.path.exists(LINK_FILE):
    with open(LINK_FILE, "r", encoding="utf-8") as f: quick_links = json.load(f)
else:
    quick_links = [{"name": "SIMBRIEF", "url": "https://www.simbrief.com/system/dispatch.php"}]

# --- Auth ---
if not st.session_state['authenticated']:
    st.title("EFBPro SYSTEM ACCESS")
    if st.text_input("ENTER ACCESS CODE", type="password") == "3910":
        st.session_state['authenticated'] = True
        st.rerun()
else:
    # --- UI Header Mode Switch ---
    if st.session_state['efb_mode'] == "BOEING":
        m_col1, m_col2 = st.columns([0.85, 0.15])
        with m_col2:
            if st.button("✈️ SW TO AIRBUS"): st.session_state['efb_mode'] = "AIRBUS"; st.rerun()

    # --- Sidebar ---
    with st.sidebar:
        st.title("EFBPro")
        if st.session_state['efb_mode'] == "AIRBUS":
            if st.button("✈️ SW TO BOEING"): st.session_state['efb_mode'] = "BOEING"; st.rerun()
        st.markdown("---")
        s_tab1, s_tab2 = st.tabs(["LINKS", "TOOLS"])
        with s_tab1:
            for l in quick_links: st.markdown(f'<a href="{l["url"]}" target="_blank" style="color:{accent_color}; text-decoration:none; font-weight:bold; display:block; margin:5px 0;">{l["name"]}</a>', unsafe_allow_html=True)
        with s_tab2:
            menu = st.radio("SELECT TOOL", ["PILOT LOCATIONS", "STOPWATCH", "OFP / AMS", "T/D CALC", "PAD", "WEATHER", "LOG", "UNIT CONVERTER", "X-WIND CALC", "VATSIM TRAFFIC"])

    # --- Main Navigation ---
    main_tab1, main_tab2, main_tab3 = st.tabs(["MAIN TOOLS", "CHECKLIST", "MAINTENANCE"])

    with main_tab1:
        if menu == "PILOT LOCATIONS":
            st.subheader("PILOT LOCATIONS")
            cols = st.columns(len(p_pos))
            for i, (airline, icao) in enumerate(p_pos.items()):
                new_icao = cols[i].text_input(f"{airline}", value=icao).upper()
                if new_icao != icao:
                    p_pos[airline] = new_icao
                    with open(POS_FILE, "w", encoding="utf-8") as f: json.dump(p_pos, f); st.rerun()

        elif menu == "STOPWATCH":
            st.subheader("STOPWATCH")
            if st.button("START"):
                st.session_state['sw_start_time'] = time.time()
                st.session_state['sw_running'] = True
            if st.button("RESET"):
                st.session_state['sw_running'] = False
                st.session_state['sw_start_time'] = 0
            if st.session_state['sw_running']:
                st.code(f"TIME: {time.strftime('%H:%M:%S', time.gmtime(time.time() - st.session_state['sw_start_time']))}")

        elif menu == "OFP / AMS":
            st.subheader("SIMBRIEF OFP & AMS PERFORMANCE")
            if st.button("FETCH FROM SIMBRIEF"):
                res = requests.get(f"https://www.simbrief.com/api/xml.fetcher.php?userid={SB_USER}&json=1")
                if res.status_code == 200:
                    st.session_state['sb_json'] = res.json()
                    st.success("IMPORTED"); st.rerun()
            
            if st.session_state.get('sb_json'):
                sb = st.session_state['sb_json']
                v1, vr, v2 = sb.get('takeoff',{}).get('v1','--'), sb.get('takeoff',{}).get('vr','--'), sb.get('takeoff',{}).get('v2','--')
                tow = sb.get('weights', {}).get('est_takeoff_weight', '0')
                
                if st.session_state['efb_mode'] == "BOEING":
                    # --- WebAMS OPERA Style Boeing UI ---
                    st.markdown(f"""
                    <div class="ams-header">
                        <div>{sb.get('atc',{}).get('callsign','--')} | {sb.get('origin',{}).get('icao_code')} ➔ {sb.get('destination',{}).get('icao_code')}</div>
                        <div>{sb.get('aircraft',{}).get('reg','--')} | {sb.get('aircraft',{}).get('icaocode')}</div>
                    </div>
                    <div style="background-color:#1c2a38; padding:15px; border:1px solid #444; border-top:none; margin-bottom:10px;">
                        <span style="color:#aaa; font-size:0.8em;">EST TOW:</span> <span class="ams-green">{int(tow)/1000:.1f} T</span>
                        <div style="display: flex; justify-content: space-around; padding-top:10px;">
                            <div>V1: <span style="font-size:1.5em; font-weight:bold;">{v1}</span></div>
                            <div>VR: <span style="font-size:1.5em; font-weight:bold;">{vr}</span></div>
                            <div>V2: <span style="font-size:1.5em; font-weight:bold;">{v2}</span></div>
                        </div>
                    </div>
                    <table class="ams-table">
                        <tr><th>EVENT</th><th>PLAN</th><th>ACTUAL</th><th>REMARKS</th></tr>
                        <tr><td>Pilot BOD</td><td>-</td><td><span class="ams-input">{datetime.now().strftime('%H:%M')}</span></td><td class="ams-green">READY</td></tr>
                        <tr><td>Cargo Loading</td><td>-</td><td><span class="ams-green">DONE</span></td><td>VIA GSX</td></tr>
                        <tr><td>Gate Release</td><td>-</td><td><span class="ams-input">--:--</span></td><td style="color:#e74c3c">PENDING</td></tr>
                    </table>
                    """, unsafe_allow_html=True)
                else:
                    st.metric("V-SPEEDS", f"V1: {v1} / VR: {vr} / V2: {v2}")
                    st.metric("TOW", f"{int(tow)/1000:.1f} T")
                st.info(f"**ROUTE:** {sb.get('general', {}).get('route', 'N/A')}")

        elif menu == "T/D CALC":
            c1, c2, c3 = st.columns(3)
            curr = c1.number_input("Current Alt", 0, 45000, 35000)
            targ = c2.number_input("Target Alt", 0, 45000, 3000)
            st.metric("T/D DISTANCE", f"{((curr - targ) / 1000) * 3:.1f} NM")

        elif menu == "PAD":
            st_canvas(stroke_width=3, stroke_color="#FFFFFF", background_color="#121212", height=400, drawing_mode="freedraw", key="canvas")
            if st.button("CLEAR"): st.rerun()

        elif menu == "WEATHER":
            icao = st.text_input("AIRPORT ICAO", "RJTT").upper()
            if icao:
                res = requests.get(f"https://metar.vatsim.net/metar.php?id={icao}")
                if res.status_code == 200: st.code(res.text)

        elif menu == "LOG":
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r") as f: logs = json.load(f)
            else: logs = []
            with st.form("log_form"):
                log_ac = st.text_input("A/C TYPE", st.session_state.get('sb_json',{}).get('aircraft',{}).get('icaocode',''))
                log_to = st.text_input("TO", st.session_state.get('sb_json',{}).get('destination',{}).get('icao_code',''))
                if st.form_submit_button("SAVE"):
                    logs.append({"date": str(datetime.now().date()), "ac": log_ac, "to": log_to, "maint": "PENDING"})
                    with open(DB_FILE, "w") as f: json.dump(logs, f); st.success("SAVED")

        elif menu == "VATSIM TRAFFIC":
             st.subheader("VATSIM ONLINE TRAFFIC")
             icao = st.text_input("AIRPORT ICAO", "RJTT").upper()
             v_res = requests.get("https://data.vatsim.net/v3/vatsim-data.json")
             if v_res.status_code == 200:
                 v_data = v_res.json()
                 pilots = [p for p in v_data.get("pilots", []) if (p.get("flight_plan",{}).get("departure") == icao or p.get("flight_plan",{}).get("arrival") == icao)]
                 for p in pilots: st.info(f"**{p['callsign']}** | {p['flight_plan']['departure']} ➔ {p['flight_plan']['arrival']}")

    with main_tab2:
        ac_type = st.selectbox("AIRCRAFT", list(cl_db.keys()))
        phase = st.radio("PHASE", list(cl_db[ac_type].keys()), horizontal=True)
        for item in cl_db[ac_type][phase]: st.checkbox(item, key=f"cl_{item}")

    with main_tab3:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f: all_logs = json.load(f)
            for idx, e in enumerate(all_logs):
                st.write(f"{e['date']} | {e['ac']} | {e['to']} | {e['maint']}")
                if e['maint'] == "PENDING" and st.button(f"RELEASE {idx}"):
                    all_logs[idx]['maint'] = "RELEASED"
                    with open(DB_FILE, "w") as f: json.dump(all_logs, f); st.rerun()

    if st.session_state['sw_running']: time.sleep(1); st.rerun()
