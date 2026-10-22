import streamlit as st
import pandas as pd
from datetime import datetime
import io
import requests
import time
import plotly.express as px

st.set_page_config(page_title="Executive Dashboard", layout="wide")

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
        
        # Rename dictionary for consistency
        rename_dict = {
            'Material Id': 'Material ID',
            'Weight': 'Weight (gr)',
            'Check-In Time': 'Check-In Time',
            'Last Update Time': 'Last Update Time',
            'Berat Est 24K': 'Est 24K (gr)',
            'Est 24K': 'Est 24K (gr)'
        }
        data = data.rename(columns=rename_dict)
        
        if 'Material ID' in data.columns:
            data = data.dropna(subset=['Material ID'])
            
        # Convert numeric columns
        if 'Weight (gr)' in data.columns:
            data['Weight (gr)'] = pd.to_numeric(data['Weight (gr)'], errors='coerce').fillna(0)
            
        if 'Est 24K (gr)' in data.columns:
            data['Est 24K (gr)'] = pd.to_numeric(data['Est 24K (gr)'], errors='coerce').fillna(0)
            
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
    # 1. KPI Summary Metrics
    completed_df = df_leader[df_leader['Current Process'] == PROCESS_LIST[-1]]
    wip_df = df_leader[df_leader['Current Process'] != PROCESS_LIST[-1]]
    
    total_weight = df_leader['Weight (gr)'].sum() if 'Weight (gr)' in df_leader.columns else 0
    completed_weight = completed_df['Weight (gr)'].sum() if 'Weight (gr)' in completed_df.columns else 0
    total_est_24k = df_leader['Est 24K (gr)'].sum() if 'Est 24K (gr)' in df_leader.columns else 0
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Total Items", len(df_leader))
    with col2:
        st.metric("WIP (Items)", len(wip_df))
    with col3:
        st.metric("Completed (Items)", len(completed_df))
    with col4:
        st.metric("Total Weight (gr)", f"{total_weight:,.2f}")
    with col5:
        st.metric("Completed Weight (gr)", f"{completed_weight:,.2f}")
    with col6:
        st.metric("Total Est 24K (gr)", f"{total_est_24k:,.2f}")

    st.divider()
    st.subheader("📍 Latest Position of Each Material")

    # 2. Interactive Bar Chart with Hover Tooltip (Plotly)
    hover_summary = df_leader.groupby('Current Process').agg(
        Count=('Material ID', 'count'),
        Material_List=('Material ID', lambda x: '<br>'.join(x.astype(str))),
        Total_Berat=('Weight (gr)', 'sum') if 'Weight (gr)' in df_leader.columns else ('Material ID', lambda x: 0)
    ).reindex(PROCESS_LIST).fillna({'Count': 0, 'Material_List': 'No materials', 'Total_Berat': 0}).reset_index()

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
                      "<b>Total Weight:</b> %{customdata[1]:,.2f} gr<br><br>" +
                      "<b>Material ID / Batch List:</b><br>%{customdata[0]}<extra></extra>",
        customdata=hover_summary[['Material_List', 'Total_Berat']].values,
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
        val = row['Current Process']
        if val == PROCESS_LIST[-1]:
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