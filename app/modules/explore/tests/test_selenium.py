import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class TestSearchByExtraField():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_search_by_extra_field(self):
    self.driver.get("http://localhost:5000/")
    self.driver.set_window_size(1850, 1053)
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(4) .align-middle:nth-child(2)").click()
    element = self.driver.find_element(By.CSS_SELECTOR, ".active .align-middle:nth-child(2)")
    actions = ActionChains(self.driver)
    actions.move_to_element(element).perform()
    element = self.driver.find_element(By.CSS_SELECTOR, "body")
    actions = ActionChains(self.driver)
    self.driver.get("http://localhost:5000/explore?query=Steals")
    time.sleep(2)
    self.driver.find_element(By.LINK_TEXT, "Spurs Ring Winners").click()