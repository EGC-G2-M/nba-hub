import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def test_show_comments():
    driver = initialize_driver()
    
    try:
        host = get_host_for_selenium_testing()
    
        driver.get(f"{host}/")
        wait_for_page_to_load(driver)
        
        driver.set_window_size(1850, 1053)
        
        driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(7) .align-middle:nth-child(2)").click()
        
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        driver.find_element(By.ID, "password").send_keys("1234")
        driver.find_element(By.ID, "submit").click()
        wait_for_page_to_load(driver)
        
        driver.get(f"{host}/doi/10.1234/spurs-ring-winners/")
        wait_for_page_to_load(driver)
        
        driver.get(f"{host}/datasets/13/comments")
        wait_for_page_to_load(driver)
        
        driver.get(f"{host}/dataset/12/comment/create?content=prueba_desde_url")
        
        print("Test Show Comments passed!")

    finally:
        close_driver(driver)
 
 
def test_reply():
    driver = initialize_driver()
    
    try:
        host = get_host_for_selenium_testing()
        
        driver.get(f"{host}/")
        wait_for_page_to_load(driver)
        
        driver.set_window_size(1850, 1053)
        
        driver.find_element(By.CSS_SELECTOR, ".nav-link:nth-child(1)").click()
        
        driver.find_element(By.ID, "email").send_keys("user2@example.com")
        driver.find_element(By.ID, "password").send_keys("1234")
        driver.find_element(By.ID, "submit").click()
        wait_for_page_to_load(driver)
        
        driver.get(f"{host}/doi/10.1234/season-2023-24/")
        wait_for_page_to_load(driver)
        
        driver.get(f"{host}/datasets/12/comments")
        wait_for_page_to_load(driver)
     
        driver.get(f"{host}/dataset/12/comment/create?content=prueba_desde_url&parent_id=7")
        wait_for_page_to_load(driver)
        
        print("Test Like Pin Reply passed!")

    finally:
        close_driver(driver)


if __name__ == "__main__":
    test_show_comments()
    test_reply()