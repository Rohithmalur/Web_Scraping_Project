"""
export.py
Utility functions for exporting
tracking results.
Author : Rohith Kumar
"""
import os
import zipfile
from io import BytesIO
import pandas as pd

# =====================================================
# Create folders
# =====================================================
EXPORT_FOLDER = "exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# =====================================================
# Excel Export
# =====================================================
def export_excel(df, filename="Tracking_Result.xlsx"):
   path = os.path.join(
       EXPORT_FOLDER,
       filename
   )
   df.to_excel(
       path,
       index=False
   )
   return path

# =====================================================
# CSV Export
# =====================================================
def export_csv(df, filename="Tracking_Result.csv"):
   path = os.path.join(
       EXPORT_FOLDER,
       filename
   )
   df.to_csv(
       path,
       index=False
   )
   return path

# =====================================================
# Excel Bytes
# (Streamlit Download)
# =====================================================
def excel_bytes(df):
   buffer = BytesIO()
   with pd.ExcelWriter(
       buffer,
       engine="openpyxl"
   ) as writer:
       df.to_excel(
           writer,
           index=False
       )
   buffer.seek(0)
   return buffer.getvalue()

# =====================================================
# CSV Bytes
# =====================================================
def csv_bytes(df):
   return df.to_csv(
       index=False
   ).encode("utf-8")

# =====================================================
# Zip PDF Folder
# =====================================================
def zip_pdf_reports(
   pdf_folder,
   zip_name="PDF_Reports.zip"
):
   zip_path = os.path.join(
       EXPORT_FOLDER,
       zip_name
   )
   with zipfile.ZipFile(
       zip_path,
       "w",
       zipfile.ZIP_DEFLATED
   ) as zipf:
       for root, dirs, files in os.walk(pdf_folder):
           for file in files:
               if file.endswith(".pdf"):
                   full_path = os.path.join(
                       root,
                       file
                   )
                   zipf.write(
                       full_path,
                       arcname=file
                   )
   return zip_path

# =====================================================
# Zip Bytes
# =====================================================
def zip_bytes(zip_path):
   with open(
       zip_path,
       "rb"
   ) as f:
       return f.read()