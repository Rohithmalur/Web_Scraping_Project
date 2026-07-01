

import streamlit as st
import pandas as pd
from io import StringIO
from maersk import scrape_maersk
from utils.export import (
   excel_bytes,
   csv_bytes,
   zip_pdf_reports,
   zip_bytes
)

st.set_page_config(
   page_title="Container Tracking Portal",
   page_icon="🚢",
   layout="wide"
)
# -----------------------------
# Title
# -----------------------------
st.title("🚢 Global Container Tracking Portal")
st.markdown("---")
# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Settings")
carrier = st.sidebar.radio(
   "Select Carrier",
   [
       "Maersk",
       "MSC",
       "CMA CGM",
       "Hapag Lloyd",
       "ONE",
       "Evergreen",
       "COSCO",
       "OOCL"
   ]
)
headless = st.sidebar.checkbox(
   "Run Browser in Headless Mode",
   value=False
)
save_pdf = st.sidebar.checkbox(
   "Download PDF Reports",
   value=True
)
st.sidebar.markdown("---")
st.sidebar.success("Version 1.0")
# -----------------------------
# Input Type
# -----------------------------
st.subheader("Container Input")
input_type = st.radio(
   "Choose Input Method",
   [
       "Single Container",
       "Paste Multiple Containers",
       "Upload Excel"
   ]
)
container_numbers = []
# -----------------------------
# Single
# -----------------------------
if input_type == "Single Container":
   single = st.text_input(
       "Container Number",
       placeholder="Example: MAEU1234567"
   )
   if single:
       container_numbers.append(single.strip().upper())
# -----------------------------
# Multiple
# -----------------------------
elif input_type == "Paste Multiple Containers":
   multi = st.text_area(
       "Paste one container per line",
       height=200,
       placeholder="""
MAEU1234567
MSCU1234567
TEMU1234567
"""
   )
   if multi:
       container_numbers = [
           x.strip().upper()
           for x in multi.splitlines()
           if x.strip()
       ]
# -----------------------------
# Excel
# -----------------------------
else:
   uploaded_file = st.file_uploader(
       "Upload Excel",
       type=["xlsx", "xls"]
   )
   if uploaded_file:
       try:
           df = pd.read_excel(uploaded_file)
           st.success("Excel Loaded Successfully")
           st.dataframe(df.head())
           column = st.selectbox(
               "Select Container Number Column",
               df.columns
           )
           container_numbers = (
               df[column]
               .dropna()
               .astype(str)
               .str.upper()
               .tolist()
           )
       except Exception as e:
           st.error(e)
# -----------------------------
# Summary
# -----------------------------
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("Carrier", carrier)
col2.metric(
   "Containers",
   len(container_numbers)
)
col3.metric(
   "PDF",
   "Yes" if save_pdf else "No"
)
# -----------------------------
# Preview
# -----------------------------
if len(container_numbers) > 0:
   st.subheader("Container Preview")
   preview_df = pd.DataFrame({
       "Container Number": container_numbers
   })
   st.dataframe(
       preview_df,
       use_container_width=True
   )
# -----------------------------
# Start Button
# -----------------------------
st.markdown("---")
start = st.button(
   "🚀 Start Tracking",
   use_container_width=True
)
# -----------------------------
# Progress
# -----------------------------
progress = st.progress(0)
status = st.empty()
log = st.empty()
# -----------------------------
# Start
# -----------------------------
if start:
   if len(container_numbers) == 0:
       st.warning("Please provide at least one container.")
   else:
       status.info("Starting Tracking...")
       if carrier == "Maersk":
           results = scrape_maersk(
               container_numbers=container_numbers,
               headless=headless,
               save_pdf_reports=save_pdf,
               progress_callback=lambda p: progress.progress(p),
               log_callback=lambda msg: log.text(msg)
           )
           status.success("Tracking Completed")
           st.success(f"Successfully processed {len(container_numbers)} containers.")
           if not results.empty:
               st.subheader("Tracking Results")
               st.dataframe(
                   results,
                   use_container_width=True
               )
               col1, col2, col3 = st.columns(3)

            # Excel
       with col1:
        st.download_button(
        "📥 Excel",
        data=excel_bytes(results),
        file_name="Maersk_Tracking.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
            # CSV
       with col2:
        st.download_button(
        "📥 CSV",
        data=csv_bytes(results),
        file_name="Maersk_Tracking.csv",
        mime="text/csv"
    )
           # ZIP PDFs
       with col3:
        if save_pdf:
          zip_path = zip_pdf_reports("reports")
          st.download_button(
            "📥 PDF ZIP",
            data=zip_bytes(zip_path),
            file_name="Maersk_PDFs.zip",
            mime="application/zip"
        )
        else:
               st.warning("No data found.")
