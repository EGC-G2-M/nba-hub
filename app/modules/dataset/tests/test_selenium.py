import pytest
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestTestautommaticrecommendations():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_testautommaticrecommendations(self):
    self.driver.get("http://localhost:5000/")
    self.driver.set_window_size(822, 895)
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()
    self.driver.find_element(By.LINK_TEXT, "Spurs Ring Winners").click()
    self.driver.find_element(By.LINK_TEXT, "View").click()
    self.driver.find_element(By.CSS_SELECTOR, ".col-md-3:nth-child(2) .btn").click()
    self.driver.find_element(By.CSS_SELECTOR, ".col-md-3:nth-child(3) .btn").click()

class TestTestuploaddataset():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_testupload_dataset(self):
    self.driver.get("http://localhost:5000/")
    self.driver.set_window_size(728, 1009)
    self.driver.find_element(By.LINK_TEXT, "Login").click()
    self.driver.find_element(By.ID, "email").click()
    self.driver.find_element(By.ID, "password").send_keys("1234")
    self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
    self.driver.find_element(By.ID, "submit").click()
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(7) .align-middle:nth-child(2)").click()
    self.driver.find_element(By.CSS_SELECTOR, ".col-xs-12").click()
    self.driver.find_element(By.ID, "title").click()
    self.driver.find_element(By.ID, "title").send_keys("prueba")
    self.driver.find_element(By.ID, "desc").click()
    self.driver.find_element(By.ID, "desc").send_keys("prueba")
    file1_path = os.path.abspath("app/modules/dataset/uvl_examples/file1.uvl")
    self.driver.find_element(By.ID, "myDropzone").click().send_keys(file1_path)
    self.driver.find_element(By.LINK_TEXT, "prueba").click()
    check = self.driver.find_element(By.ID, "agreeCheckbox")
    check.send_keys(Keys.SPACE)
    upload_btn = self.driver.find_element(By.ID, "upload_button")
    upload_btn.send_keys(Keys.RETURN)
    time.sleep(2)