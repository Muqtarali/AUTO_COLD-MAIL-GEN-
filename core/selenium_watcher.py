"""Selenium-based Gmail watcher to detect replies when IMAP misses them.

Notes:
- Requires a signed-in Chrome profile. Set env GMAIL_SELENIUM_PROFILE to a Chrome user-data-dir
  that is already logged into Gmail (no 2FA prompts). Example on Windows:
    GMAIL_SELENIUM_PROFILE=C:\\Users\\user\\AppData\\Local\\Google\\Chrome\\User Data
- Requires chromedriver available on PATH or CHROME_DRIVER_PATH env pointing to the driver.
- This watcher is heuristic and may break if Gmail DOM changes; it should be considered a best-effort
  fallback when IMAP does not detect the reply.
"""
import os
import threading
import time
import logging
from typing import Callable, Dict, Set

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

class SeleniumGmailWatcher:
    def __init__(self, poll_interval: int = 45):
        self.poll_interval = poll_interval
        self.driver = None
        self.threads: Dict[str, threading.Thread] = {}
        self.processed_keys: Set[str] = set()
        self.lock = threading.Lock()

    def _get_driver(self):
        if self.driver:
            return self.driver

        options = Options()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("detach", True)

        profile_dir = os.getenv("GMAIL_SELENIUM_PROFILE")
        if profile_dir:
            options.add_argument(f"--user-data-dir={profile_dir}")
        else:
            logger.warning("GMAIL_SELENIUM_PROFILE not set; Gmail login may fail if not already authenticated.")

        driver_path = os.getenv("CHROME_DRIVER_PATH")
        service = Service(driver_path) if driver_path else Service()
        self.driver = webdriver.Chrome(service=service, options=options)
        return self.driver

    def start_watch(self, conversation_id: str, recipient_email: str, subject: str, callback: Callable[[str, str, str], None]):
        if conversation_id in self.threads:
            logger.info(f"Selenium watcher already running for {conversation_id}")
            return

        thread = threading.Thread(
            target=self._watch_loop,
            args=(conversation_id, recipient_email, subject, callback),
            daemon=True,
        )
        self.threads[conversation_id] = thread
        thread.start()
        logger.info(f"Started Selenium watcher for conversation {conversation_id}")

    def stop_watch(self, conversation_id: str):
        if conversation_id in self.threads:
            del self.threads[conversation_id]
            logger.info(f"Stopped Selenium watcher for conversation {conversation_id}")

    def _watch_loop(self, conversation_id: str, recipient_email: str, subject: str, callback: Callable[[str, str, str], None]):
        query = f"from:{recipient_email} subject:\"{subject}\""
        driver = self._get_driver()

        while conversation_id in self.threads:
            try:
                search_url = f"https://mail.google.com/mail/u/0/#search/{query.replace(' ', '%20')}"
                driver.get(search_url)

                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='main']"))
                    )
                except Exception:
                    logger.warning(f"Selenium watcher {conversation_id}: search page did not load")
                    time.sleep(self.poll_interval)
                    continue

                rows = driver.find_elements(By.CSS_SELECTOR, "div[role='main'] tr.zA")
                logger.info(f"Selenium watcher {conversation_id}: found {len(rows)} rows for query {query}")

                if not rows:
                    time.sleep(self.poll_interval)
                    continue

                # Inspect the top rows (most recent first)
                for row in rows[:5]:
                    try:
                        subj_el = row.find_element(By.CSS_SELECTOR, "span.bog")
                        subj_text = subj_el.text.strip().lower()
                        from_el = row.find_element(By.CSS_SELECTOR, "span.yP") if row.find_elements(By.CSS_SELECTOR, "span.yP") else None
                        from_text = from_el.get_attribute("email") if from_el else ""
                        snippet_el = row.find_element(By.CSS_SELECTOR, "span.y2") if row.find_elements(By.CSS_SELECTOR, "span.y2") else None
                        snippet_text = snippet_el.text.strip() if snippet_el else ""

                        key = f"{subj_text}|{from_text}|{snippet_text}"
                        with self.lock:
                            if key in self.processed_keys:
                                continue

                        if subject.lower() not in subj_text:
                            continue

                        # Open the email to extract body
                        row.click()
                        try:
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.a3s"))
                            )
                            body_divs = driver.find_elements(By.CSS_SELECTOR, "div.a3s")
                            body_text = "\n".join([d.text for d in body_divs if d.text]).strip()
                        except Exception:
                            body_text = snippet_text or ""

                        logger.info(
                            f"Selenium watcher {conversation_id}: detected reply from {from_text} subject={subj_text} snippet={snippet_text[:80]}"
                        )
                        callback(conversation_id, recipient_email, body_text)

                        with self.lock:
                            self.processed_keys.add(key)

                        driver.back()
                        break
                    except Exception as e:
                        logger.warning(f"Selenium watcher {conversation_id}: row parse error {e}")
                        continue

            except Exception as e:
                logger.error(f"Selenium watcher {conversation_id} error: {e}")
            time.sleep(self.poll_interval)

# Global singleton
_selenium_watcher = SeleniumGmailWatcher()

def get_selenium_watcher() -> SeleniumGmailWatcher:
    return _selenium_watcher
