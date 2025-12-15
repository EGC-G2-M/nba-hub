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

class TestShowComments():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_showComments(self):
    self.driver.get("http://localhost:5000/")
    self.driver.set_window_size(1850, 1053)
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(7) .align-middle:nth-child(2)").click()
    self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
    self.driver.find_element(By.ID, "password").send_keys("1234")
    self.driver.find_element(By.ID, "submit").click()
    self.driver.find_element(By.LINK_TEXT, "Spurs Ring Winners").click()
    self.driver.get("http://localhost:5000/datasets/13/comments")
    self.driver.find_element(By.CSS_SELECTOR, ".justify-content-between > .btn").click()
    self.driver.find_element(By.ID, "commentContent").click()
    self.driver.find_element(By.ID, "commentContent").send_keys("prueba")
    self.driver.find_element(By.ID, "submit").click()
    
class TestLIkePinReply():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_lIkePinReply(self):
    self.driver.get("http://localhost:5000/")
    self.driver.set_window_size(1850, 1053)
    self.driver.find_element(By.CSS_SELECTOR, ".nav-link:nth-child(1)").click()
    self.driver.find_element(By.ID, "email").send_keys("user2@example.com")
    self.driver.find_element(By.ID, "password").send_keys("1234")
    self.driver.find_element(By.ID, "submit").click()
    self.driver.find_element(By.LINK_TEXT, "Season 2023-24").click()
    self.driver.get("http://localhost:5000/datasets/12/comments")
    self.driver.find_element(By.CSS_SELECTOR, ".comment-card:nth-child(1) .d-flex > .d-flex > .d-inline:nth-child(1) svg").click()
    self.driver.find_element(By.CSS_SELECTOR, ".comment-card:nth-child(1) .d-flex > .d-flex > .d-inline:nth-child(1) svg").click()
    self.driver.find_element(By.CSS_SELECTOR, ".comment-card:nth-child(1) .d-flex > .btn").click()
    self.driver.find_element(By.ID, "commentContent").click()
    self.driver.find_element(By.ID, "commentContent").send_keys("prueba")
    self.driver.find_element(By.ID, "submit").click()
    self.driver.find_element(By.CSS_SELECTOR, ".comment-card:nth-child(1) .ms-3 > .d-flex > .d-inline:nth-child(2) path").click()
    self.driver.find_element(By.CSS_SELECTOR, ".comment-card:nth-child(1) .ms-3 > .d-flex > .d-inline:nth-child(1) svg").click()
