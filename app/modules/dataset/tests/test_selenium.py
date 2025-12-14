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
    self.driver.set_window_size(1920, 1080)
    self.driver.find_element(By.LINK_TEXT, "Login").click()
    self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
    self.driver.find_element(By.ID, "password").send_keys("1234")
    self.driver.find_element(By.ID, "submit").click()
    self.driver.find_element(By.LINK_TEXT, "Spurs Ring Winners").click()
    self.driver.find_element(By.LINK_TEXT, "View").click()
    self.driver.find_element(By.LINK_TEXT, "View").click()

class TestTestuploaddataset():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
    
  def teardown_method(self, method):
    self.driver.quit()

  def test_testupload_dataset(self):
    self.driver.get("http://localhost:5000/")
    self.driver.set_window_size(1920, 1080)
    
    # --- LOGIN ---
    self.driver.find_element(By.LINK_TEXT, "Login").click()
    self.driver.find_element(By.ID, "email").click()
    self.driver.find_element(By.ID, "password").send_keys("1234")
    self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
    self.driver.find_element(By.ID, "submit").click()
    
    # --- NAVEGACIÓN A UPLOAD ---
    # Nota: Ajusta estos selectores si cambian en tu menú lateral
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(7) .align-middle:nth-child(2)").click() 
    self.driver.find_element(By.CSS_SELECTOR, ".col-xs-12").click()
    
    # --- INFO BÁSICA DEL DATASET ---
    self.driver.find_element(By.ID, "title").click()
    self.driver.find_element(By.ID, "title").send_keys("Bucks Season Stats")
    self.driver.find_element(By.ID, "desc").click()
    self.driver.find_element(By.ID, "desc").send_keys("Estadísticas de temporada regular")
    self.driver.find_element(By.NAME, "tags").send_keys("nba, bucks")
    
    # --- PREPARAR ARCHIVOS ---
    file1_path = os.path.abspath("app/modules/dataset/csv_examples/east-regular-season-champs/bucks_2020-21.csv")
    file2_path = os.path.abspath("app/modules/dataset/csv_examples/east-regular-season-champs/bucks_2022-23.csv")
    
    # --- SOLUCIÓN DROPZONE (EVITA ERROR NOT INTERACTABLE) ---
    # 1. Encontrar el input oculto
    dropzone_input = self.driver.find_element(By.CLASS_NAME, "dz-hidden-input")
    
    # 2. Hacerlo visible con JS
    self.driver.execute_script(
        "arguments[0].style.visibility = 'visible'; arguments[0].style.display = 'block'; arguments[0].style.height = '1px'; arguments[0].style.width = '1px'; arguments[0].style.opacity = 1;",
        dropzone_input
    )
    
    # 3. Enviar los dos archivos
    dropzone_input.send_keys(file1_path)
    
    # --- SUBIR (CHECKBOX Y BOTÓN) ---
    check = self.driver.find_element(By.ID, "agreeCheckbox")
    # Scroll y click seguro
    self.driver.execute_script("arguments[0].scrollIntoView(true);", check)
    self.driver.execute_script("arguments[0].click();", check)
    
    upload_btn = self.driver.find_element(By.ID, "upload_button")
    
    # Esperamos que el botón se habilite
    self.driver.execute_script("arguments[0].click();", upload_btn)
    
    # Espera pequeña para asegurar que la petición se envía antes de cerrar el test
    time.sleep(2)
    
class TestTrendingDataset():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_testselenium(self):
    self.driver.get("http://localhost:5000/")
    self.driver.set_window_size(966, 1095)
    self.driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()
    self.driver.find_element(By.LINK_TEXT, "Trending Datasets").click()
  