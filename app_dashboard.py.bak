import streamlit as st
import pandas as pd
from datetime import datetime
import io
import requests
import time
import plotly.express as px

st.set_page_config(page_title="Production Executive Dashboard", layout="wide")

# Google Sheets Link
URL_ASLI_SHEET = "https://docs.google.com/spreadsheets/d/1haDJKJFD_o4tOwXSE4kw4wXHjnfM9UCo3LwQXztrWLk/edit?usp=sharing"

PROCESS_LIST = [
    "1. Material Receiving",
    "2. Gold Leaf Making",
    "3. Aquaregia Process",
    "4. Reduction Aquaregia",
    "5. Au Sponge Cleaning",
    "6. Granulating",
    "7. ICP Testing",
    "8. Cast Bar Making"
]

def load_data():
    try:
        if "/edit" in URL_ASLI_SHEET:
            base_url = URL_ASLI_SHEET.split("/edit")[0]
        else:
            base_url = URL_ASLI_SHEET
            
        url_realtime = f"{base_url}/export?format=csv&t={int(time.time())}"
        response = requests.get(url_realtime, timeout=10)
        
        if "html" in response.headers.get('Content-Type', '').lower() or "<!doctype html>" in response.text.lower():
            st.error("🔒 Google Sheets Access Locked or Invalid Link.")
            return pd.DataFrame()
            
        raw_data = io.StringIO(response.text)
        data = pd.read_csv(raw_data, on_bad_lines='skip')
        
        # Trim whitespace from column names
        data.columns = [str(col).strip() for col in data.columns]
        
        # Map exact columns from Google Sheet
        rename_dict = {
            'Material ID': 'Material ID',
            'Material Type': 'Material Type',
            'Weight': 'Weight (gr)',
            'Purity': 'Purity (%)',
            '24K Est': 'Est 24K (gr)',
            'Check-In Time': 'Check-In Time',
            'Current Process': 'Current Process',
            'Last Update Time': 'Last Update Time'
        }
        data = data.rename(columns=rename_dict)
        
        if 'Material ID' in data.columns:
            data = data.dropna(subset=['Material ID'])
            
        # Clean numeric formatting (e.g. "60,143.32" -> 60143.32)
        for col in ['Weight (gr)', 'Purity (%)', 'Est 24K (gr)']:
            if col in data.columns:
                data[col] = data[col].astype(str).str.replace(',', '').str.replace('%', '').str.strip()
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
            else:
                data[col] = 0.0

        # Fallback calculation for Est 24K if zero
        if 'Est 24K (gr)' in data.columns and 'Purity (%)' in data.columns and 'Weight (gr)' in data.columns:
            mask = (data['Est 24K (gr)'] == 0) & (data['Purity (%)'] > 0)
            data.loc[mask, 'Est 24K (gr)'] = data.loc[mask, 'Weight (gr)'] * (data.loc[mask, 'Purity (%)'] / 100.0)
            
        return data
    except Exception as e:
        st.error(f"⚠️ Synchronization issue detected: {e}")
        return pd.DataFrame()

df_leader = load_data()

st.title("📊 Production Executive Dashboard")
st.markdown("Real-time monitoring summary for Management")
st.divider()

if df_leader.empty or 'Current Process' not in df_leader.columns:
    st.info("⌛ Connecting to Google Sheets...")
else:
    # Clean string column
    df_leader['Current Process'] = df_leader['Current Process'].astype(str).str.strip()
    
    # 1. KPI Summary Metrics
    target_completed_process = PROCESS_LIST[-1].strip()
    completed_df = df_leader[df_leader['Current Process'] == target_completed_process]
    wip_df = df_leader[df_leader['Current Process'] != target_completed_process]
    
    # Convert weights from Grams to Kilograms (1 Kg = 1000 gr)
    total_weight_kg = df_leader['Weight (gr)'].sum() / 1000.0
    completed_weight_kg = completed_df['Weight (gr)'].sum() / 1000.0
    total_est_24k_kg = df_leader['Est 24K (gr)'].sum() / 1000.0
    wip_est_24k_kg = wip_df['Est 24K (gr)'].sum() / 1000.0
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        st.metric("Total Items", len(df_leader))
    with col2:
        st.metric("WIP (Items)", len(wip_df))
    with col3:
        st.metric("Completed (Items)", len(completed_df))
    with col4:
        st.metric("Total Weight (Kg)", f"{total_weight_kg:,.2f}")
    with col5:
        st.metric("Completed Weight (Kg)", f"{completed_weight_kg:,.2f}")
    with col6:
        st.metric("Total Est 24K (Kg)", f"{total_est_24k_kg:,.2f}")
    with col7:
        st.metric("WIP Est 24K (Kg)", f"{wip_est_24k_kg:,.2f}")

    st.divider()
    st.subheader("📍 Latest Position of Each Material")

    # 2. Interactive Bar Chart with Hover Tooltip (Plotly)
    hover_summary = df_leader.groupby('Current Process').agg(
        Count=('Material ID', 'count'),
        Material_List=('Material ID', lambda x: '<br>'.join(x.astype(str))),
        Total_Berat=('Weight (gr)', 'sum')
    ).reindex(PROCESS_LIST).fillna({'Count': 0, 'Material_List': 'No materials', 'Total_Berat': 0}).reset_index()

    # Convert chart summary weight to Kg
    hover_summary['Total_Berat_Kg'] = hover_summary['Total_Berat'] / 1000.0

    fig = px.bar(
        hover_summary,
        x='Current Process',
        y='Count',
        labels={'Current Process': 'Process Stage', 'Count': 'Material Count'},
        title="Material Distribution per Process Stage",
        text='Count',
        color_discrete_sequence=['#1f77b4']
    )

    fig.update_traces(
        hovertemplate="<b>Process:</b> %{x}<br>" +
                      "<b>Item Count:</b> %{y}<br>" +
                      "<b>Total Weight:</b> %{customdata[1]:,.3f} Kg<br><br>" +
                      "<b>Material ID / Batch List:</b><br>%{customdata[0]}<extra></extra>",
        customdata=hover_summary[['Material_List', 'Total_Berat_Kg']].values,
        textposition='outside'
    )

    fig.update_layout(
        xaxis_tickangle=-30,
        height=450,
        margin=dict(l=20, r=20, t=50, b=50)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 3. Live Monitoring Data Table
    st.markdown("### Live Monitoring Data Table")
    def highlight_process(row):
        val = str(row['Current Process']).strip()
        if val == target_completed_process:
            color = 'background-color: #d4edda; color: #155724;' # Green for completed
        else:
            color = 'background-color: #cce5ff; color: #004085;' # Blue for WIP
        styles = [''] * len(row)
        if 'Current Process' in row.index:
            styles[row.index.get_loc('Current Process')] = color
        return styles

    styled_df = df_leader.style.apply(highlight_process, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # 4. Export Features
    st.divider()
    st.markdown("### 📥 Download Production Reports")
    col_dl1, col_dl2, _ = st.columns(3)
    
    csv_data = df_leader.to_csv(index=False).encode('utf-8')
    with col_dl1:
        st.download_button(label="📄 Download Data (CSV)", data=csv_data, file_name=f"executive_report_{datetime.now().strftime('%Y%m%d')}.csv", mime='text/csv', use_container_width=True)
        
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_leader.to_excel(writer, index=False, sheet_name='Material Data')
    excel_data = buffer.getvalue()
    with col_dl2:
        st.download_button(label="🟢 Download Data (Excel)", data=excel_data, file_name=f"executive_report_{datetime.now().strftime('%Y%m%d')}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)