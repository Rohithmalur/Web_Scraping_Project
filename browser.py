"""
browser.py
Browser utility functions
Uses the same browser initialization
as the original RPA project.
"""
import os
import base64
import time
import shutil
#import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ======================================================
# Clear UC Cache
# ======================================================
def clear_uc_cache():
   cache = os.path.expanduser(
       "~/.undetected_chromedriver"
   )
   if os.path.exists(cache):
       try:
           shutil.rmtree(cache)
           print("UC Cache Cleared")
       except Exception:
           pass

# ======================================================
# Launch Browser
# ======================================================
def launch_browser(headless=True):
   options = Options()
   if headless:
       options.add_argument("--headless=new")
   options.binary_location = "/usr/bin/chromium"
   options.add_argument("--no-sandbox")
   options.add_argument("--disable-dev-shm-usage")
   options.add_argument("--disable-gpu")
   options.add_argument("--window-size=1920,1080")
   options.add_argument("--remote-debugging-port=9222")
   service = Service("/usr/bin/chromedriver")
   driver = webdriver.Chrome(
       service=service,
       options=options
   )
   driver.set_page_load_timeout(60)
   return driver
   

"""def launch_browser(headless=True):
   clear_uc_cache()
   options = uc.ChromeOptions()
   if headless:
       options.add_argument("--headless=new")
   options.binary_location = "/usr/bin/chromium"
   options.add_argument("--no-sandbox")
   options.add_argument("--disable-dev-shm-usage")
   options.add_argument("--disable-gpu")
   options.add_argument("--disable-dev-tools")
   options.add_argument("--no-zygote")
   options.add_argument("--single-process")
   options.add_argument("--window-size=1920,1080")
   options.add_argument("--disable-blink-features=AutomationControlled")
   driver = uc.Chrome(
       options=options,
       browser_executable_path="/usr/bin/chromium",
       driver_executable_path="/usr/bin/chromedriver",
       use_subprocess=True
   )
   driver.set_page_load_timeout(60)
   return driver"""

# ======================================================
# Wait Element
# ======================================================
def wait_for_element(
   driver,
   by,
   value,
   timeout=20
):
   return WebDriverWait(
       driver,
       timeout
   ).until(
       EC.presence_of_element_located(
           (by, value)
       )
   )

# ======================================================
# Safe Click
# ======================================================
def safe_click(
   driver,
   xpath,
   timeout=10
):
   try:
       button = WebDriverWait(
           driver,
           timeout
       ).until(
           EC.element_to_be_clickable(
               (By.XPATH, xpath)
           )
       )
       button.click()
       return True
   except:
       return False

# ======================================================
# Accept Cookies
# ======================================================
def accept_cookies(driver):
   xpaths = [
       "//button[contains(.,'Allow all')]",
       "//button[contains(.,'Accept')]",
       "//button[contains(.,'Accept All')]",
       "//button[contains(.,'I Agree')]"
   ]
   for xpath in xpaths:
       if safe_click(driver, xpath, 5):
           print("Cookies Accepted")
           time.sleep(1)
           return

# ======================================================
# Save PDF
# ======================================================
def save_pdf(
   driver,
   output_path
):
   pdf = driver.execute_cdp_cmd(
       "Page.printToPDF",
       {
           "printBackground": True,
           "landscape": False
       }
   )
   with open(output_path, "wb") as f:
       f.write(
           base64.b64decode(
               pdf["data"]
           )
       )

# ======================================================
# Close Browser
# ======================================================
def close_browser(driver):
   try:
       driver.quit()
   except:
       pass
