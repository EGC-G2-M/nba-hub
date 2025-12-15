import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver


def wait_for_page_to_load(driver, timeout=4):
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def test_check_csv():
    driver = initialize_driver()
    wait = WebDriverWait(driver, 10)

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/doi/10.1234/spurs-ring-winners/")
        wait_for_page_to_load(driver)
        
        driver.set_window_size(1854, 923)

        check_buttons = driver.find_elements(By.CSS_SELECTOR, "button[id^='btnGroupDrop']:not([id^='btnGroupDropExport'])")
        
        for btn in check_buttons[:2]:
            btn_id = btn.get_attribute('id')
            
            file_id = btn_id.replace('btnGroupDrop', '')
            
            btn.click()
            
            menu_anchor = driver.find_element(By.CSS_SELECTOR, f"ul[aria-labelledby='{btn_id}'] a")
            menu_anchor.click()
            
            wait.until(EC.visibility_of_element_located((By.ID, f"check_{file_id}")))
            
            badge = driver.find_element(By.CSS_SELECTOR, f"#check_{file_id} .badge.bg-success").text
            assert badge.strip() == "Valid Model"
            
        print("Test Check CSV passed!")

    finally:
        close_driver(driver)


if __name__ == "__main__":
    test_check_csv()