import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def test_search_by_extra_field():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/")
        wait_for_page_to_load(driver)
        
        driver.set_window_size(1850, 1053)

        driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(4) .align-middle:nth-child(2)").click()

        element = driver.find_element(By.CSS_SELECTOR, ".active .align-middle:nth-child(2)")
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()

        element = driver.find_element(By.CSS_SELECTOR, "body")
        actions = ActionChains(driver) 

        driver.get(f"{host}/explore?query=Steals")
        wait_for_page_to_load(driver)
        
        time.sleep(2)

        driver.get(f"{host}/doi/10.1234/spurs-ring-winners/")
        
        print("Test Search By Extra Field passed!")

    finally:
        close_driver(driver)


if __name__ == "__main__":
    test_search_by_extra_field()