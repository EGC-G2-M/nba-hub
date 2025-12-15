import os
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


def get_downloads_count(driver):
    text = driver.find_element(By.ID, "dataset_downloads_count").text
    return int(text.split(":")[1].strip())


def test_counter_selenium():
    driver = initialize_driver()
    wait = WebDriverWait(driver, 10)

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/")
        driver.set_window_size(1854, 923)
        driver.get(f"{host}/doi/10.1234/spurs-ring-winners/")
        
        wait.until(EC.presence_of_element_located((By.ID, "dataset_downloads_count")))
        initial_downloads = get_downloads_count(driver)
        
        driver.find_element(By.CSS_SELECTOR, ".d-block").click()
        driver.find_element(By.LINK_TEXT, "Download (2.65 KB)").click()
        driver.get(f"{host}/doi/10.1234/spurs-ring-winners/")

        wait.until(lambda d: get_downloads_count(driver) == initial_downloads + 1)
        downloads_after_single = get_downloads_count(driver)
        
        assert downloads_after_single == initial_downloads + 1

        elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[id^="btnGroupDropExport"]')))
        elem.click()
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "CSV"))).click()
        
        driver.find_element(By.CSS_SELECTOR, ".col-xl-8").click()
        driver.find_element(By.LINK_TEXT, "Download all (2.65 KB)").click()
        driver.find_element(By.CSS_SELECTOR, ".card:nth-child(2) > .card-body").click()
        driver.find_element(By.CSS_SELECTOR, ".d-block").click()
        driver.get(f"{host}/doi/10.1234/spurs-ring-winners/")
        
        wait.until(EC.presence_of_element_located((By.ID, "dataset_downloads_count")))
        final_downloads = get_downloads_count(driver)

        assert final_downloads == downloads_after_single
        print("Test Counter Selenium passed!")

    finally:
        close_driver(driver)


def test_automatic_recommendations():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/")
        driver.set_window_size(1920, 1080)
        
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        driver.find_element(By.ID, "password").send_keys("1234")
        driver.find_element(By.ID, "submit").click()
        
        driver.get(f"{host}/doi/10.1234/spurs-ring-winners/")
        driver.find_element(By.LINK_TEXT, "View").click()
        driver.find_element(By.LINK_TEXT, "View").click()
        
        print("Test Automatic Recommendations passed!")

    finally:
        close_driver(driver)


def test_upload_dataset_custom():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/")
        driver.set_window_size(1920, 1080)
        
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.ID, "email").click()
        driver.find_element(By.ID, "password").send_keys("1234")
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        driver.find_element(By.ID, "submit").click()
        
        driver.find_element(By.CSS_SELECTOR, ".sidebar-item:nth-child(7) .align-middle:nth-child(2)").click() 
        driver.find_element(By.CSS_SELECTOR, ".col-xs-12").click()
        
        driver.find_element(By.ID, "title").click()
        driver.find_element(By.ID, "title").send_keys("Bucks Season Stats")
        driver.find_element(By.ID, "desc").click()
        driver.find_element(By.ID, "desc").send_keys("Estadísticas de temporada regular")
        driver.find_element(By.NAME, "tags").send_keys("nba, bucks")
        
        file1_path = os.path.abspath("app/modules/dataset/csv_examples/east-regular-season-champs/bucks_2020-21.csv")
        
        dropzone_input = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        
        driver.execute_script(
            "arguments[0].style.visibility = 'visible'; arguments[0].style.display = 'block'; arguments[0].style.height = '1px'; arguments[0].style.width = '1px'; arguments[0].style.opacity = 1;",
            dropzone_input
        )
        
        dropzone_input.send_keys(file1_path)
        
        check = driver.find_element(By.ID, "agreeCheckbox")
        
        driver.execute_script("arguments[0].scrollIntoView(true);", check)
        driver.execute_script("arguments[0].click();", check)
        
        upload_btn = driver.find_element(By.ID, "upload_button")
        
        driver.execute_script("arguments[0].click();", upload_btn)
        
        time.sleep(2)
        
        print("Test Upload Dataset Custom passed!")

    finally:
        close_driver(driver)


def test_trending_dataset():
    driver = initialize_driver()
    wait = WebDriverWait(driver, 10)

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/")
        driver.set_window_size(966, 1095)
        
        driver.find_element(By.CSS_SELECTOR, ".sidebar-toggle").click()
        
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Trending Datasets")))
        driver.find_element(By.LINK_TEXT, "Trending Datasets").click()

        print("Test Trending Dataset passed!")

    finally:
        close_driver(driver)


if __name__ == "__main__":
    test_counter_selenium()
    test_automatic_recommendations()
    test_upload_dataset_custom()
    test_trending_dataset()