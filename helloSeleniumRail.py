from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
#to maxinise the broser window
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome("C:/chromeDriver/chromedriver.exe",chrome_options=options)

driver.get("https://www.amadeusrail.net/")
time.sleep(5)
driver.quit()