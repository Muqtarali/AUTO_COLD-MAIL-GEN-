# core/scrape.py
from __future__ import annotations
import time
from typing import Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.parsers import clean_html_text

def _headless_driver() -> webdriver.Chrome:
    """
    Create a headless Chrome driver using a locally installed chromedriver.
    Make sure chromedriver is installed and on PATH.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def scrape_job_url(url: str, timeout: int = 25) -> Tuple[str, str]:
    """
    Fetch a job posting URL and return (raw_html, cleaned_text).
    """
    d = _headless_driver()
    try:
        d.get(url)
        WebDriverWait(d, timeout).until(lambda drv: drv.execute_script("return document.readyState") == "complete")
        WebDriverWait(d, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(0.7)  # let dynamic content settle a bit
        html = d.page_source
        text = clean_html_text(html)
        return html, text
    finally:
        d.quit()

__all__ = ["scrape_job_url"]
