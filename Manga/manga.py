from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from PyPDF2 import PdfMerger
from PIL import Image
from time import sleep
from datetime import datetime
import requests, os, json
import undetected_chromedriver as uc

DELAY = 20

headers = {
    'authority': 'img.mghubcdn.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}

class MangaService():
    def __init__(self, siteToOpen, mangaName, numberOfChapters):
        self._mangaName = mangaName
        self._numberOfChapters = numberOfChapters

        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options = uc.ChromeOptions()
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--load-extension=./adblock')
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

        self._driver = uc.Chrome(user_data_dir='F:\Proiecte\Proiecte_py\Scripts\profile', options=chrome_options, desired_capabilities=desired_capabilities)#, headless=True)
        self._driver.maximize_window()
        sleep(2)
        self._closePopup()
        self._driver.get(siteToOpen)

    def _waitForElement(self, stringToWait, mode = By.XPATH, type = EC.presence_of_element_located):
        try:
            WebDriverWait(self._driver, DELAY).until(type((mode, stringToWait)))
        except TimeoutException:
            self._driver.quit()

    def _closePopup(self):
        numberOfTabs = len(self._driver.window_handles)
        if numberOfTabs> 1:
            self._driver.switch_to.window(self._driver.window_handles[numberOfTabs - 1])
            self._driver.close()
            self._driver.switch_to.window(self._driver.window_handles[0])  
   
    def _writeChapter(self, lastChapter):
        with open('manga.json', 'r+') as file:
            file_data = json.load(file)
            file_data["chapters"][self._mangaName] =  lastChapter
            file.seek(0)
            json.dump(file_data, file)

    def _readChapter(self):
        with open('manga.json', 'r') as file:
            file_data = json.load(file)
            try:
                lastChapter = file_data["chapters"][self._mangaName]
            except KeyError:
                lastChapter = 0
        return lastChapter

    def _searchManga(self):
        sleep(2)
        self._waitForElement('//*[@id="q"]')
        self._driver.find_element(By.XPATH, '//*[@id="q"]').send_keys(self._mangaName)
        self._driver.find_element(By.XPATH, '//*[@id="q"]').send_keys(Keys.ENTER)

    def _selectManga(self):
        sleep(1)
        self._waitForElement('//*[@id="app"]/div[1]/div[1]/div[2]/div[1]')
        try:
            listOfMangas = self._driver.find_elements(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[2]/div')
        except NoSuchElementException:
            print('No manga after this name\n')
            return -1

        print("Select a manga to download. ", end="")
        for count in range(0, 5):
            sleep(1)
            print(count, end=" ")
        try:
            self._driver.find_elements(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[2]/div')
            listOfMangas[0].find_element(By.CSS_SELECTOR, 'div > div.media-body > h4 > a').click()
        except:
            pass
        
        return 0

    def _goToFirstChapter(self):
        sleep(1)
        if len(self._driver.window_handles) > 1:
            self._closePopup()

        sleep(1)
        self._waitForElement('//*[@id="mangadetail"]/section[1]/div[2]/div/div[2]/h1')
        self._mangaName = self._driver.find_element(By.XPATH, '//*[@id="mangadetail"]/section[1]/div[2]/div/div[2]/h1').text.splitlines()[0].lower()
        buttons = self._driver.find_elements(By.XPATH, '//*[@id="mangadetail"]/section[1]/div[2]/div/div[2]/div[2]/div[2]/a')
        
        if len(buttons) == 1:
            buttons[0].click()
        else:
            buttons[1].click()

    def _getCookies(self):
        self._driver.refresh()
        sleep(4)
        self._waitForElement('/html/body/img')
        cookies = self._driver.get_cookies()
        self._driver.close()

        for cookie in cookies:
            if 'cf_clearance' == cookie['name']:
                return { cookie['name']: cookie['value'] }

    def _getLinkToImages(self):
        self._waitForElement('//*[@id="mangareader"]/div[1]/div/img[1]')
        firstChapterName = self._driver.find_element(By.XPATH, '//*[@id="mangareader"]/div[1]/h3').text
        firstChapterNumber = int(firstChapterName[firstChapterName.find('#') + 1])

        chapterCount = self._readChapter()
        if 0 == chapterCount:
            chapterCount = firstChapterNumber

        linkToImages = self._driver.find_element(By.XPATH, '//*[@id="mangareader"]/div[1]/div/img[1]').get_attribute('src')
        self._driver.get(linkToImages)
        return linkToImages.replace(f'{firstChapterNumber}/1.jpg', f'{chapterCount}/1.jpg')

    def _downloadManga(self):
        if not os.path.exists('./manga/' + self._mangaName):
            os.makedirs('./manga/' + self._mangaName)
        imagesToAdd = []
        finished = False
        imageCount = 1
        linkToImages= self._getLinkToImages()
        chapterCount = int(linkToImages[-7])
        requestCookies = self._getCookies()
        exitFlag = 0

        for _ in range(0, self._numberOfChapters):
            while True:
                response = requests.get(linkToImages, cookies=requestCookies, headers=headers)
                if 404 == response.status_code:
                    response = requests.get(linkToImages.replace('.jpg', '.png'), cookies=requestCookies, headers=headers)
                if 403 == response.status_code:
                    self._driver.get(linkToImages)
                    requestCookies = self._getCookies()
                    exitFlag += 1
                    if 10 <= exitFlag:
                        print(403)
                        finished = True
                        break
                    continue
                elif 404 == response.status_code:
                    if imageCount == 1:
                        finished = True
                    break

                with open(f'manga/{self._mangaName}/{imageCount}.jpg', 'wb') as f:
                    f.write(response.content)

                linkToImages = linkToImages.replace(f'{chapterCount}/{imageCount}.jpg', f'{chapterCount}/{imageCount + 1}.jpg')
                imageCount += 1
                exitFlag = 0

            if finished:
                break

            imagesToAdd.append(self._saveToPdf(imageCount))
            print(datetime.now().strftime("%H:%M:%S"), f'Finished chapter {chapterCount}')
            linkToImages = linkToImages.replace(f'{chapterCount}/{imageCount}.jpg', f'{chapterCount + 1}/1.jpg')
            chapterCount += 1
            imageCount = 1

        self._writeChapter(chapterCount)
        os.rmdir('./manga/' + self._mangaName)
        os.rmdir('./manga')

        return imagesToAdd

    def _mergePdf(self):
        merger = PdfMerger()
        merger.append(f'mangaBooks/{self._mangaName}_manga.pdf')
        merger.append(f'mangaBooks/{self._mangaName}_manga_new.pdf')
        merger.write(f'mangaBooks/{self._mangaName}_manga_2.pdf')
        merger.close()
        os.remove(f'mangaBooks/{self._mangaName}_manga.pdf')
        os.remove(f'mangaBooks/{self._mangaName}_manga_new.pdf')
        os.rename(f'mangaBooks/{self._mangaName}_manga_2.pdf', f'mangaBooks/{self._mangaName}_manga.pdf')

    def _saveToPdf(self, numberOfImages):
        images = []
        for count in range(1, numberOfImages):
            images.append(Image.open(f'manga/{self._mangaName}/{count}.jpg'))

        minWidth = min(image.width for image in images)
        imagesResized = [image.resize((minWidth, int(image.height * minWidth / image.width))) for image in images]
        totalHeight = sum(image.height for image in imagesResized)
        imageToSave = Image.new('RGB', (minWidth, totalHeight))
        pos_y = 0
        count = 1
        for image in imagesResized:
            imageToSave.paste(image, (0, pos_y))
            pos_y += image.height
            image.close()
            os.remove(f'manga/{self._mangaName}/{count}.jpg')
            count += 1

        return imageToSave

    def _saveManga(self, imagesToAdd):
        pdfPath = f'mangaBooks/{self._mangaName}_manga_new.pdf'

        if len(imagesToAdd) == 0:
            return
    
        if len(imagesToAdd) > 1:
            imagesToAdd[0].save(pdfPath, "PDF", resolution=100.0, save_all=True, append_images=imagesToAdd[1:])
        else:
            imagesToAdd[0].save(pdfPath, "PDF", resolution=100.0, save_all=True)

        if os.path.exists(f'mangaBooks/{self._mangaName}_manga.pdf'):
            self._mergePdf()

    def run(self):
        print("searching manga...")
        self._searchManga()
        print("selecting manga...")
        if self._selectManga() < 0:
            self._driver.quit()
            return
        print("first chap manga...")
        self._goToFirstChapter()
        print("downloading manga...")
        allImages = self._downloadManga()
        self._saveManga(allImages)
        self._driver.quit()

if __name__ == '__main__':
    with open('mangaToGet.txt', 'r') as mangaFile:
        mangaName = mangaFile.read()
    numberOfChapters = 10
    srv = MangaService('https://mangahub.io/search//', mangaName, numberOfChapters)
    srv.run()