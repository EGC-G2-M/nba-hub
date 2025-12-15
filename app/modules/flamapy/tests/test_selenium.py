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
 
class TestCheckcsv():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_checkcsv(self):
    # Navegar directamente a la vista del dataset (más fiable que buscar en la lista)
    self.driver.get("http://localhost:5000/doi/10.1234/spurs-ring-winners/")
    self.driver.set_window_size(1854, 923)
    wait = WebDriverWait(self.driver, 10)
 
    # Encontrar hasta 5 botones de 'Check' y ejecutar la comprobación de sintaxis para cada uno
    # Seleccionar solamente los botones 'Check' (no los 'Export')
    check_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[id^='btnGroupDrop']:not([id^='btnGroupDropExport'])")
    for btn in check_buttons[:2]:
        btn_id = btn.get_attribute('id')
        # Extraer el id numérico del archivo asociado
        file_id = btn_id.replace('btnGroupDrop', '')
        # Abrir el menú y seleccionar 'Syntax check' dentro del menú específico
        btn.click()
        menu_anchor = self.driver.find_element(By.CSS_SELECTOR, f"ul[aria-labelledby='{btn_id}'] a")
        menu_anchor.click()
        # Esperar que el área de comprobación para ese archivo sea visible
        wait.until(expected_conditions.visibility_of_element_located((By.ID, f"check_{file_id}")))
        badge = self.driver.find_element(By.CSS_SELECTOR, f"#check_{file_id} .badge.bg-success").text
        assert badge.strip() == "Valid Model"