from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
#this method will hight the element
def highlight(element):
    """Highlights (blinks) a Selenium Webdriver element"""
    driver = element._parent
    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                              element, s)
    original_style = element.get_attribute('style')
    apply_style("background: yellow; border: 2px solid red;")
    time.sleep(.3)
    apply_style(original_style)

#global variable
path='C:\PythonInput\PaymentURL.txt'#file path
#runTimeinMinutes=5 # 5 minutes from now


#read file to find the Amadeus Payment page URL for the defined time
runSelenium=None#controls if Selenium script will run or not
#timeout = time.time() + 60*runTimeinMinutes
#print("Program will run for "+str(runTimeinMinutes)+" minutes.")
print("Welcome to Selenium Script Automation Tool for TTS")
try:
    while True:
        while True:#while loop nto check file in every 5 secs
            URLFile = open(path,'r')
            contents = URLFile.read().splitlines()#read line by line alos strip /n newline charactre
            if(contents!=''):
                for content in contents:
                    print(content.strip())
                    URL=content.strip()
                    runSelenium=True
                    URLFile.close()
            if(runSelenium):
                break #break the while loop if URL is found
            if(runSelenium!=True):
                print("URL is not found. Sleeping for 5 secs. Press CTRL+C to close to exit.")
                time.sleep(5)
            URLFile.close()#close the file in every loop

        # Start selenium scripts
        # to maxinise the broser window
        if (runSelenium):
            options = Options()
            options.add_argument("--start-maximized")
            driver = webdriver.Chrome("C:/chromeDriver/chromedriver.exe", chrome_options=options)
            driver.implicitly_wait(30)  # Adding 30seconds implicit wait
            driver.get(URL)
            pageTitle = driver.title
            print ("Page Title:" + pageTitle)
            # find all elements related to Credit card payment and fill up the form
            try:
                CardTypeDropDownBox = Select(driver.find_element_by_xpath("//select[@name='vendor']"))
                CardTypeDropDownBox.select_by_visible_text("MasterCard")#select Master Card
                #EnterNamber
                creditCardNumberInputBox = driver.find_element_by_xpath("//input[@id='pan']")
                highlight(creditCardNumberInputBox)
                creditCardNumberInputBox.send_keys("5100081112223332")

                creditCardHolderNameInputBox = driver.find_element_by_xpath("//input[@id='creditcard_holdername']")
                highlight(creditCardHolderNameInputBox)
                creditCardHolderNameInputBox.send_keys("TEST")

                YearDropDownBox = Select(driver.find_element_by_xpath("//select[@name='year']"))
                #highlight(YearDropDownBox)
                YearDropDownBox.select_by_visible_text("2018")

                MonthDropDownBox = Select(driver.find_element_by_xpath("//select[@name='month']"))
                #highlight(MonthDropDownBox)
                MonthDropDownBox.select_by_visible_text("August")

                CVVInputBox = driver.find_element_by_xpath("//input[@id='creditcard_cvv']")
                highlight(CVVInputBox)
                CVVInputBox.send_keys("737")

                BuyNowButton = driver.find_element_by_xpath("//span[text()='Buy now']")
                highlight(BuyNowButton)
                BuyNowButton.click()
                time.sleep(15)  # spleeps for 15 secs
                #to do write logic to close browser based on the sucess criteria
                driver.quit()
            except:
                print ("Some Error")
                driver.quit()

        # End selenium script

        # open the URl file and make delete the line to get it back to initial state
        if (runSelenium):
            URLFile = open(path, 'w')
            URLFile.write('')
            URLFile.close()
            runSelenium = None

except KeyboardInterrupt:
    print("Closing the script. Bye Bye....")
    time.sleep(2)





