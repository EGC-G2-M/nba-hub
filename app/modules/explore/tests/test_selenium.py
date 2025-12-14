import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver

class TestFilterByExtraField:
    
    def setup_method(self, method):
        self.driver = initialize_driver()
        self.host = get_host_for_selenium_testing()

    def teardown_method(self, method):
        close_driver(self.driver)

    def wait_for_page_to_load(self, timeout=4):
        """Helper para esperar a que la página cargue completamente."""
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def test_filterByExtraField(self):
        driver = self.driver
        host = self.host
        
        driver.get(f"{host}/")
        self.wait_for_page_to_load()
        
        driver.set_window_size(706, 923)
        driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()
        driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(4) .align-middle:nth-child(2)").click()
        self.wait_for_page_to_load()
        
        query_input = driver.find_element(By.ID, "query")
        query_input.click()
        query_input.send_keys("Steals")
        
        time.sleep(1) 
        
        driver.find_element(By.LINK_TEXT, "Spurs Ring Winners").click()
        self.wait_for_page_to_load()
        
        print("Test FilterByExtraField passed!")