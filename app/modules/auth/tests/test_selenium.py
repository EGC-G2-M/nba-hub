import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def test_logina():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/") 
        wait_for_page_to_load(driver)

        driver.set_window_size(1165, 917)

        driver.find_element(By.LINK_TEXT, "Login").click()
        wait_for_page_to_load(driver)
        driver.find_element(By.ID, "submit").click()
        
        driver.find_element(By.ID, "email").click()
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        
        driver.find_element(By.ID, "submit").click()
        
        driver.find_element(By.CSS_SELECTOR, ".row:nth-child(3) .mb-3").click()
        
        driver.find_element(By.ID, "password").click()
        driver.find_element(By.ID, "password").send_keys("1")
        driver.find_element(By.ID, "submit").click()
        
        driver.find_element(By.ID, "password").click()
        driver.find_element(By.ID, "password").send_keys("1234")
        
        driver.find_element(By.ID, "submit").click()
        wait_for_page_to_load(driver)

        driver.find_element(By.LINK_TEXT, "Log out").click()
        wait_for_page_to_load(driver)

        print("Test passed!")

    finally:
        close_driver(driver)

test_logina()