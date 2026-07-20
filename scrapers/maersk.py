"""
maersk.py
Maersk Web Scraper
Author : Rohith Kumar
Version : 1.0
"""
"""from scrapers.browser import launch_browser
from scrapers.browser import accept_cookies
from scrapers.browser import save_pdf
from scrapers.browser import close_browser
"""

import os
import time
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
from browser import (
   launch_browser,
   close_browser,
   accept_cookies,
   save_pdf
)
# ======================================================
# CONSTANTS
# ======================================================
BASE_URL = "https://www.maersk.com/tracking/"
TODAY = datetime.today().strftime("%Y%m%d")
PDF_FOLDER = f"reports/Maersk_{TODAY}"
os.makedirs(PDF_FOLDER, exist_ok=True)

# ======================================================
# MAIN FUNCTION
# ======================================================
def scrape_maersk(
   container_numbers,
   headless=False,
   save_pdf_reports=True,
   progress_callback=None,
   log_callback=None
):
   """
   Parameters
   ----------
   container_numbers : list
   headless : bool
   save_pdf_reports : bool
   progress_callback :
       Streamlit Progress Bar
   log_callback :
       Streamlit Logger
   Returns
   -------
   DataFrame
   """
   all_results = []
   total = len(container_numbers)
   driver = launch_browser(headless)
   cookies_accepted = False
   try:
       # =============================================
       # LOOP CONTAINERS
       # =============================================
       for index, container in enumerate(container_numbers):
           if log_callback:
               log_callback(
                   f"Processing {container}"
               )
           url = BASE_URL + container
           driver.get(url)
           # Accept cookies only once
           if not cookies_accepted:
               accept_cookies(driver)
               cookies_accepted = True
           # Give page a moment to stabilize
           time.sleep(2)
           # -----------------------------------------
           # Save PDF
           # -----------------------------------------
           if save_pdf_reports:
               pdf_name = os.path.join(
                   PDF_FOLDER,
                   f"{container}_{TODAY}.pdf"
               )
               save_pdf(
                   driver,
                   pdf_name
               )
           # -----------------------------------------
           # Extract Data
           # (Implemented in Section 2)
           # -----------------------------------------
           shipment_data = extract_container_data(
               driver,
               container
           )
           if shipment_data:
               all_results.extend(
                   shipment_data
               )
           # -----------------------------------------
           # Progress
           # -----------------------------------------
           if progress_callback:
               progress = int(
                   ((index + 1) / total) * 100
               )
               progress_callback(progress)
       df = pd.DataFrame(all_results)
       return df
   finally:
       close_browser(driver)

# ======================================================
# SECTION 2 PLACEHOLDER
# ======================================================
def extract_container_data(driver, container):
   """
   This function will
   1. Read Shipment Header
   2. Read Origin/Destination
   3. Read Timeline
   4. Parse Events
   5. Return List of Dictionaries
   """
   return []

# ======================================================
# SECTION 3 PLACEHOLDER
# ======================================================
def parse_timeline(
   container_text,
   container,
   ship_from,
   ship_to,
   equipment,
   last_updated
):
   """
   Timeline Parser
   Implemented in Section 3
   """
   return []

# ======================================================
# SECTION 2
# Extract Shipment Details
# ======================================================
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_container_data(driver, container):
   """
   Extract all information for one container
   Returns a list of dictionaries
   """
   try:
       # Wait until timeline is available
       WebDriverWait(driver, 25).until(
           EC.presence_of_element_located(
               (By.ID, "transport-plan__container__0")
           )
       )
   except Exception as e:
       print(f"{container} : Timeline not found")
       return []
   # ---------------------------------------------
   # Timeline Text
   # ---------------------------------------------
   try:
       container_text = driver.find_element(
           By.ID,
           "transport-plan__container__0"
       ).text
   except:
       container_text = ""
   # ---------------------------------------------
   # Shipment Summary
   # ---------------------------------------------
   try:
       shipment_summary = driver.find_element(
           By.CLASS_NAME,
           "search-summary-ocean__locations"
       ).text
   except:
       shipment_summary = ""
   # ---------------------------------------------
   # Container Header
   # ---------------------------------------------
   try:
       container_header = driver.find_element(
           By.CLASS_NAME,
           "container__header"
       ).text
   except:
       container_header = ""
   # =================================================
   # Ship From
   # =================================================
   ship_from = "Not Available"
   if "From" in shipment_summary:
       try:
           ship_from = (
               shipment_summary
               .split("From", 1)[1]
               .split("To", 1)[0]
               .strip()
           )
       except:
           pass
   # =================================================
   # Ship To
   # =================================================
   ship_to = "Not Available"
   if "To" in shipment_summary:
       try:
           ship_to = shipment_summary.split(
               "To",
               1
           )[1].strip()
       except:
           pass
   # =================================================
   # Equipment Type
   # =================================================
   equipment_type = "Not Available"
   try:
       header_parts = container_header.split("|")
       if len(header_parts) > 1:
           equipment_type = (
               header_parts[1]
               .split("Last")[0]
               .strip()
           )
   except:
       pass
   # =================================================
   # Last Updated
   # =================================================
   last_updated = "Not Available"
   if "Last updated:" in container_header:
       try:
           last_updated = (
               container_header
               .split("Last updated:", 1)[1]
               .strip()
           )
       except:
           pass
   # =================================================
   # Parse Timeline
   # =================================================
   return parse_timeline(
       container_text=container_text,
       container=container,
       ship_from=ship_from,
       ship_to=ship_to,
       equipment=equipment_type,
       last_updated=last_updated
   )


# ======================================================
# SECTION 3
# Timeline Parser
# ======================================================
def parse_timeline(
   container_text,
   container,
   ship_from,
   ship_to,
   equipment,
   last_updated
):
   """
   Convert Maersk timeline text into structured records.
   Returns
   -------
   List[Dict]
   """
   rows = []
   import_date = pd.Timestamp(datetime.now())
   if not container_text:
       return rows
   # ---------------------------------------------
   # Clean Timeline
   # ---------------------------------------------
   lines = [
       line.strip()
       for line in container_text.splitlines()
       if line.strip()
   ]
   location = ""
   terminal = ""
   months = [
       "Jan", "Feb", "Mar", "Apr",
       "May", "Jun", "Jul", "Aug",
       "Sep", "Oct", "Nov", "Dec"
   ]
   i = 0
   while i < len(lines):
       current_line = lines[i]
       # -----------------------------------------
       # Detect Location
       # -----------------------------------------
       if (
           current_line.isupper()
           and len(current_line) > 2
       ):
           location = current_line
           i += 1
           continue
       # -----------------------------------------
       # Detect Terminal
       # -----------------------------------------
       if "terminal" in current_line.lower():
           terminal = current_line
           i += 1
           continue
       # -----------------------------------------
       # Detect Event
       # -----------------------------------------
       if (
           i + 1 < len(lines)
           and any(
               month in lines[i + 1]
               for month in months
           )
       ):
           event = current_line
           datetime_text = lines[i + 1]
           parts = datetime_text.rsplit(" ", 1)
           event_date = ""
           event_time = ""
           if len(parts) == 2:
               event_date = parts[0]
               event_time = parts[1]
           elif len(parts) == 1:
               event_date = parts[0]
           row = {
               "Extract Date": import_date,
               "Carrier": "Maersk",
               "Container Number": container,
               "Ship From": ship_from,
               "Ship To": ship_to,
               "Equipment Type": equipment,
               "Last Updated": last_updated,
               "Location": location,
               "Terminal": terminal,
               "Event": event,
               "Date": event_date,
               "Time": event_time
           }
           rows.append(row)
           i += 2
       else:
           i += 1
   return rows


# ======================================================
# SECTION 4
# Production Ready Main Scraper
# ======================================================
def scrape_maersk(
   container_numbers,
   headless=False,
   save_pdf_reports=True,
   progress_callback=None,
   log_callback=None,
   retry_count=2
):
   """
   Scrape multiple Maersk containers
   Parameters
   ----------
   container_numbers : list
   headless : bool
   save_pdf_reports : bool
   progress_callback : function(int)
   log_callback : function(str)
   retry_count : int
   Returns
   -------
   pandas.DataFrame
   """
   all_results = []
   total = len(container_numbers)
   driver = launch_browser(headless)
   cookies_accepted = False
   failed_containers = []
   try:
       for index, container in enumerate(container_numbers):
           success = False
           for attempt in range(retry_count + 1):
               try:
                   if log_callback:
                       log_callback(
                           f"Processing {container} "
                           f"(Attempt {attempt+1})"
                       )
                   driver.get(BASE_URL + container)
                   if not cookies_accepted:
                       accept_cookies(driver)
                       cookies_accepted = True
                   # Allow page to stabilize
                   time.sleep(2)
                   # -----------------------------
                   # Save PDF
                   # -----------------------------
                   if save_pdf_reports:
                       pdf_path = os.path.join(
                           PDF_FOLDER,
                           f"{container}_{TODAY}.pdf"
                       )
                       save_pdf(driver, pdf_path)
                   # -----------------------------
                   # Extract
                   # -----------------------------
                   rows = extract_container_data(
                       driver,
                       container
                   )
                   if rows:
                       all_results.extend(rows)
                   success = True
                   break
               except Exception as e:
                   if log_callback:
                       log_callback(
                           f"Retry {attempt+1} failed : {e}"
                       )
                   time.sleep(2)
           if not success:
               failed_containers.append(container)
           if progress_callback:
               percent = int(
                   ((index + 1) / total) * 100
               )
               progress_callback(percent)
       df = pd.DataFrame(all_results)
       # -----------------------------------------
       # Remove duplicates
       # -----------------------------------------
       if not df.empty:
           df = df.drop_duplicates()
       # -----------------------------------------
       # Sort
       # -----------------------------------------
       if "Container Number" in df.columns:
           df = df.sort_values(
               by=[
                   "Container Number",
                   "Date"
               ]
           )
       # -----------------------------------------
       # Log failed containers
       # -----------------------------------------
       if len(failed_containers) > 0:
           print("\nFailed Containers")
           for x in failed_containers:
               print(x)
       return df
   finally:
       close_browser(driver)


       # ======================================================

# Export Excel

# ======================================================
def export_excel(df, filename):
    df.to_excel(
        filename,
        index=False
    )
# ======================================================
# Export CSV
# ======================================================
def export_csv(df, filename):
    df.to_csv(
        filename,
        index=False
    )
# ======================================================
# Save Failed Containers
# ======================================================
def save_failed(
    failed_list,
    filename="failed_containers.csv"
):
    if len(failed_list) == 0:
        return
    pd.DataFrame(
        {
            "Container Number": failed_list
        }
    ).to_csv(
        filename,
        index=False
    )
