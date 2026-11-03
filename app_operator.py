import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

st.set_page_config(
    page_title="Operator Checklist - Production Floor", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Webhook URL for Google Apps Script (Appends data to 'Checklist_Log' tab)
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzFdETw5CLY6NvqzeH8U1x8bTnWCaGOQpzGY8idhVJNXLoj4egNc9wvC7vpQzOBloEr/exec"

st.title("🛠️ Operator Daily Checklist Form")
st.caption("Connected to Google Sheets tab: Checklist_Log (gid=802911412)")
st.divider()

# ==============================================================================
# 1. PROCESS STAGE SELECTION
# ==============================================================================
selected_process = st.selectbox(
    "Select Production Process Stage:",
    [
        "1. Melting (Banting Centrifugal)",
        "2. Aquaregia Process (Reactor)",
        "3. Transfer to Reduction Tank",
        "4. Gold Filtering & Chemical Reduction",
        "5. Gold Granule Making",
        "6. Cast Bar Making"
    ]
)

st.divider()

# ==============================================================================
# 2. HSE/K3 WARNINGS & CHECKLIST ITEMS PER PROCESS
# ==============================================================================
CHECKLIST_ITEMS = []

if "Melting" in selected_process:
    st.subheader("Stage: Melting (Centrifugal Banting)")
    st.warning("""
    ⚠️ **SAFETY WARNING (HSE):**  
    Do NOT drain or open the chamber door if the internal temperature is above **370°C**!
    """)
    CHECKLIST_ITEMS = [
        "1. Center piece hole cleanliness (Free of scale/residue)",
        "2. Lower chamber seal (LOCKED & tightly sealed)",
        "3. Melting chamber seal (LOCKED & tightly sealed)",
        "4. Water chiller circulation (Smooth flow, hoses unkinked)",
        "5. Crucible condition (No cracks, proper wall thickness)",
        "6. Stopper closure condition (Normal mechanical operation)",
        "7. Centrifugal rotation test (Symmetrical at 55% ratio)",
        "8. Initial Chiller Water Temp (Target: 25°C)",
        "9. Initial vacuum check (Stable 30s initial draw)",
        "10. Initial Nitrogen supply (Normal pressure for 30s)",
        "11. Melting target temp reach (Limit: 1050°C)",
        "12. Pouring temp lowering & hold (Stable at 970°C)",
        "13. Rapid cooling Nitrogen shift (From 6 bar to 10 bar)",
        "14. Safe machine chamber draining limit (Cooled to 370°C)"
    ]

elif "Aquaregia" in selected_process:
    st.subheader("Stage: Aquaregia in Reactor")
    st.warning("""
    ⚠️ **SAFETY WARNING (HSE):**  
    Mandatory full acid/gas PPE required (**Respirator, Chemical Gloves, Goggles**) during reactor operation!
    """)
    CHECKLIST_ITEMS = [
        "1. Check reactor chamber for leaks",
        "2. Verify sufficient stock of HNO3 and HCL",
        "3. Verify demin water stock supply",
        "4. Inspect water chiller unit functionality",
        "5. Ensure aspirator position is set to LOW",
        "6. Test HCL miscelation air flow functionality",
        "7. Verify HCL & HNO3 flowmeter calibration",
        "8. Test Oxygen gas supply line",
        "9. Load banting material into reactor barrel",
        "10. Lock Reactor 1 & Reactor 2 covers tightly",
        "11. Input operational parameters on control panel",
        "12. Execute cycle (10-hour cycle / Temp < 40°C)"
    ]

elif "Transfer to Reduction" in selected_process:
    st.subheader("Stage: Transfer to Reduction Tank")
    st.warning("""
    ⚠️ **SAFETY WARNING (HSE):**  
    Check SR & Reduction valves for leaks before starting pump. Wear safety goggles and acid apron!
    """)
    CHECKLIST_ITEMS = [
        "1. [PRE] Check filter condition (NOT CLOGGED)",
        "2. [PRE] Inspect SR Tank physical condition (NO LEAKS)",
        "3. [PRE] Inspect Reduction Tank physical condition (NO LEAKS)",
        "4. Turn on SR pump & set air pressure to 2 - 2.5 bar",
        "5. Open reactor valve until liquid fully transfers to SR",
        "6. Stop SR pump once liquid transfer is verified complete",
        "7. Turn on AGCL chamber pump & open valve to SR tank",
        "8. Carefully open top reactor lid",
        "9. Close filter valve & add 10L demin water (1:1 ratio)",
        "10. Allow liquid to settle for 2 - 4 hours",
        "11. Turn on aspirator damper & set level to MEDIUM",
        "12. Flush internal reactor walls using demin water",
        "13. Close bottom reactor valve & clean remaining AR in AGCL",
        "14. Stop pump, close SR valve & add demin water per ratio",
        "15. Start reduction pump, open filter valve, transfer liquid to tank",
        "16. Clean SR tank & reduction filter with demin water, stop pump"
    ]

elif "Gold Filtering" in selected_process:
    st.subheader("Stage: Gold Filtering & Chemical Reduction")
    st.warning("""
    ⚠️ **SAFETY WARNING (HSE):**  
    **NOX gas is highly toxic and corrosive!** Ensure damper opening is exactly at **Position 3** and suction aspirator is fully active before starting reduction.
    """)
    CHECKLIST_ITEMS = [
        "1. Check SMB reductant stock & volume (200 g/L)",
        "2. Verify mechanical damper opening at Position 3",
        "3. Set mixer speed precisely to 3 Step",
        "4. Input sodium parameter for Stage I reaction",
        "5. Start Stage I sodium parameter",
        "6. Monitor Stage I reduction until NOX gas vents safely",
        "7. Input sodium parameter for Stage II reaction",
        "8. Start Stage II sodium parameter",
        "9. Monitor aquaregia color change to clear yellow",
        "10. Perform circulation & add small sodium amount if cloudy",
        "11. Open allocated Tank S (1, 2, 3, 4) valves",
        "12. Start main booster pump & open Tank P (1, 2) valves",
        "13. Flush & wash down brown powder using demin water pipe"
    ]

elif "Granule" in selected_process:
    st.subheader("Stage: Gold Granule Making")
    st.warning("""
    ⚠️ **SAFETY WARNING (HSE):**  
    HIGH TEMPERATURE HAZARD (**700°C - 900°C**)! Heat-resistant gloves and face shield are mandatory during metal pouring.
    """)
    CHECKLIST_ITEMS = [
        "1. Check water chiller and flow readiness (Normal/Unclogged)",
        "2. Check melting chamber water supply readiness",
        "3. Ensure crucible container is 100% clean of metal residue",
        "4. Prepare 1 large basin and 4 small non-metallic basins",
        "5. Prepare paper lining for stainless oven tray",
        "6. Carefully transfer brown powder into small non-metallic basin",
        "7. Turn on melting unit heating element",
        "8. Feed brown powder into upper chamber gradually (do not overload)",
        "9. Increase temp gradually from 700°C to 900°C (5-10°C intervals)",
        "10. Close upper chamber after powder is fully loaded until molten",
        "11. Release stopper lever and ensure liquid fully drains",
        "12. Drain and clean water from melting chamber unit",
        "13. Divide wet granules into 4 small non-metallic basins & wipe dry",
        "14. Oven dry granules at 100°C - 150°C for 1.5 - 2 hours",
        "15. Drain/cool granules for 30 - 50 mins until ready for weighing"
    ]

elif "Cast Bar" in selected_process:
    st.subheader("Stage: Cast Bar Making")
    st.warning("""
    ⚠️ **SAFETY WARNING (HSE):**  
    HIGH TEMPERATURE & MOLTEN METAL HAZARD! Wear full aluminized heat suit, heavy duty heat gloves, face shield, and safety boots.
    """)
    CHECKLIST_ITEMS = [
        "1. Ensure analytical scale is clean and daily calibrated",
        "2. Weigh gold granules according to target order (100g, 1kg, etc.)",
        "3. Verify mold/molding condition is clean with zero slag residue",
        "4. Check & set Inner plate temp set-point to 73°C",
        "5. Check & set Outer plate temp set-point to 80°C",
        "6. Configure VMF converter set-point to standard 92%",
        "7. Monitor Max opening inner plate tolerance (Max 19%)",
        "8. Monitor Max opening outer plate tolerance (Max 17%)",
        "9. Run heating cycle with target Melting time for 480 – 500 s",
        "10. Pour liquid pure gold into mold, cool down, and weigh final bar"
    ]

# ==============================================================================
# 3. OPERATOR INPUT FORM
# ==============================================================================
with st.form("form_checklist_operator"):
    st.markdown("### 📋 Operational Header Data")
    
    col1, col2 = st.columns(2)
    with col1:
        work_date = st.date_input("Work Order Date:", datetime.now())
        nama_operator = st.text_input("Operator Name:", placeholder="Enter your full name...")
        
    with col2:
        nomor_batch = st.text_input("Material Batch Code:", placeholder="e.g., BATCH-2026-001")
        kode_mesin = st.text_input("Machine / Station Code:", placeholder="e.g., MCN-01 / Reactor 1")
        verifikator_qc = st.text_input("QC / Field Verifier Name:", placeholder="QC inspector name...")

    st.divider()
    st.markdown("### ⚙️ SOP Inspection Checklist Items")

    checklist_results = {}
    for idx, item_text in enumerate(CHECKLIST_ITEMS, 1):
        c_text, c_status = st.columns([3, 1])
        with c_text:
            st.write(f"**{item_text}**")
        with c_status:
            checklist_results[f"Item_{idx}"] = st.radio(
                f"Status_{idx}", 
                ["OK", "REJ"], 
                horizontal=True, 
                label_visibility="collapsed",
                key=f"item_{idx}_{selected_process}"
            )
        st.markdown("---")

    catatan_kendala = st.text_area(
        "Field Remarks / Issue Notes:", 
        placeholder="Record any operational anomalies, errors, or maintenance notes here..."
    )

    submit_button = st.form_submit_button("📤 Submit Daily Checklist to Sheet", use_container_width=True)

    if submit_button:
        if not nama_operator or not nomor_batch or not kode_mesin:
            st.error("❌ **Submission Failed:** Operator Name, Batch Code, and Machine Code are mandatory fields!")
        else:
            total_rej = sum(1 for val in checklist_results.values() if val == "REJ")
            status_akhir = "NORMAL / PASSED" if total_rej == 0 else f"WARNING ({total_rej} Item REJ)"
            timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Payload format sent to Google Apps Script -> 'Checklist_Log' tab (gid=802911412)
            payload = {
                "timestamp": timestamp_now,
                "tanggal": str(work_date),
                "proses": selected_process,
                "batch": nomor_batch,
                "operator": nama_operator,
                "kode_mesin": kode_mesin,
                "qc_verifikator": verifikator_qc,
                "status_akhir": status_akhir,
                "catatan": catatan_kendala
            }

            try:
                response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
                if response.status_code == 200 and response.json().get("result") == "success":
                    st.success("🎉 **Checklist Data Successfully Logged to Google Sheets (Checklist_Log)!**")
                    st.balloons()
                else:
                    st.error(f"❌ Failed to write to Google Sheets. Response: {response.text}")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")