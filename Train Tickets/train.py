from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
import json

DELAY = 30

with open("train.json", "r") as jsonFile:
    user = json.load(jsonFile)

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

service = Service('./driver/chromedriver.exe')
service.start()

serviceArguments = ["--incognito", "--verbose", "--log-path=driver/chromedriver.log"]

driver = webdriver.Chrome(service=service, options=chrome_options, service_args=serviceArguments)
driver.maximize_window()
driver.get('https://www.cfrcalatori.ro/en/')

try:
    WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.ID, 'input-station-departure-name')))
except TimeoutException:
    print("eroare info")
    driver.quit()
    exit()

driver.find_element(By.ID, 'input-station-departure-name').send_keys('Cluj Napoca')
driver.find_element(By.ID, 'input-station-arrival-name').send_keys('Suceava')

try:
    WebDriverWait(driver, DELAY).until(EC.visibility_of_element_located((By.ID, 'ui-id-2')))
except TimeoutException:
    print("eroare info")
    driver.quit()
    exit()

driver.execute_script("document.getElementById('ui-id-2').style.display = 'none';")
driver.execute_script("document.getElementById('dataPleca').value = '02.10.2022';")
driver.find_element(By.XPATH, '//*[@id="form-search"]/div[3]/button').click()
driver.switch_to.window(driver.window_handles[0])
driver.close()
driver.switch_to.window(driver.window_handles[0])

try:
    WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div[2]/main/div/div[3]/ul/li')))
except TimeoutException:
    print("eroare info")
    driver.quit()
    exit()

driver.find_element(By.ID, 'button-allow-cookie').click()
trainList = driver.find_elements(By.XPATH, '/html/body/div[2]/div/div[2]/main/div/div[3]/ul/li')
number = 1

for train in trainList:
    toPrint = '[' + str(number) + ']\t'
    number += 1
    toPrint += train.text
    toPrint = toPrint.replace("\n", "  ")
    toPrint = toPrint + "\n"
    print(toPrint)

trainToGo = int(input("Selecteaza trenul: "))
trainList[trainToGo - 1].find_element(By.ID, 'button-itinerary-' + str(trainToGo - 1) + '-buy').click()

try:
    WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.ID, 'button-next-step-2')))
    driver.find_element(By.ID, 'button-next-step-2').click()
except TimeoutException:
    print("eroare info")
    driver.quit()
    exit()

try:
    WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.ID, 'button-ticket-fare-4-more')))
    driver.find_element(By.ID, 'button-ticket-fare-4-more').click()
    WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[2]/main/div/div[3]/form/div[2]/div[1]/div/div/div[13]/div/div/div[3]/button')))
    driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/main/div/div[3]/form/div[2]/div[1]/div/div/div[13]/div/div/div[3]/button').click()
    WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.ID, 'button-next-step-3')))
    driver.find_element(By.ID, 'button-next-step-3').click()
except TimeoutException:
    print("eroare info")
    driver.quit()
    exit()
    
try:
    WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.ID, 'button-next-step-4')))
    driver.find_element(By.ID, 'button-next-step-4').click()
except TimeoutException:
    print("eroare info")
    driver.quit()
    exit()

try:
    WebDriverWait(driver, DELAY).until(EC.visibility_of_element_located((By.ID, 'UserName')))
    driver.find_element(By.ID, 'UserName').send_keys(user['userName'])
    driver.find_element(By.ID, 'Password').send_keys(user['password'])
    driver.find_element(By.ID, 'button-login').click()
    sleep(1)
    WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.ID, 'button-next-step-5')))
    driver.find_element(By.ID, 'button-next-step-5').click()
except TimeoutException:
    print("eroare info")
    driver.quit()
    exit()

try:
    WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.ID, 'button-confirm-selection')))
    driver.find_element(By.ID, 'button-confirm-selection').click()
    WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.ID, 'button-next-step-6')))
    driver.find_element(By.ID, 'button-next-step-6').click()
except TimeoutException:
    print("eroare info")
    driver.quit()
    exit()

try:
    WebDriverWait(driver, DELAY).until(EC.visibility_of_element_located((By.ID, 'input-passenger-0-fidelity-card')))
    driver.find_element(By.ID, 'input-passenger-0-fidelity-card').send_keys(user['onlineId'])
    driver.find_element(By.ID, 'input-passenger-0-identity-number').send_keys(user['cnp'])
    WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.ID, 'button-next-step-7')))
    driver.find_element(By.ID, 'button-next-step-7').click()
except TimeoutException:
    print("eroare info")
    driver.quit()
    exit()

try:
    WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.ID, 'card')))
    driver.find_element(By.ID, 'card').send_keys(user['cardNumber'])
    driver.find_element(By.ID, 'name_on_card').send_keys(user['cardName'])
    monthExpiration = Select(driver.find_element(By.ID, 'exp_month'))
    yearExpiration = Select(driver.find_element(By.ID, 'exp_year'))
    monthExpiration.select_by_value(user['monthExpiration'])
    yearExpiration.select_by_value(user['yearExpiration'])
    driver.find_element(By.ID, 'cvv2').send_keys(user['cvv2'])
    driver.find_element(By.ID, 'consent').click()
except TimeoutException:
    print("eroare info")
    driver.quit()
    exit()

input("Press to quit:\n")
driver.quit()