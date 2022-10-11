from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
import undetected_chromedriver as uc
import random

DELAY = 20

class WebSiteController:
    def __init__(self, siteToOpen) -> None:
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options = uc.ChromeOptions()
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--load-extension=./adblock')

        self._driver = uc.Chrome(user_data_dir='F:\Proiecte\Proiecte_py\Scripts\profile', options=chrome_options)
        self._driver.maximize_window()
        self._driver.get(siteToOpen)

    def _waitForElement(self, stringToWait, mode = By.XPATH, type = EC.presence_of_element_located):
        try:
            WebDriverWait(self._driver, DELAY).until(type((mode, stringToWait)))
        except TimeoutException:
            self._driver.quit()

    def quit(self):
        self._driver.quit()
    
    def getFeedback(self, row):
        elements = self._driver.find_elements(By.XPATH, f'/html/body/main/div[1]/div[{row}]/div')
        lettersState = []
        for el in elements:
            lettersState.append(el.get_attribute('class')[5])
        return lettersState

    def sendWord(self, word):
        print("Trying " + word, end="")
        for letter in word:
            ActionChains(self._driver).send_keys(letter).perform()
            sleep(0.2)

    def tryAgain(self):
        self._driver.refresh()
        self._waitForElement('/html/body/main/div[1]')


class WordleSolver:
    def __init__(self, controller) -> None:
        self._correctLetters = {}
        self._goodLetters = {}
        self._badLetters = []
        self._controller = controller
    
    def _verifyLine(self, line):
        for letter in self._badLetters:
            if letter in line:
                if letter not in self._goodLetters.keys() and letter not in self._correctLetters.keys():
                    return False
                elif line.count(letter) > 1:
                    return False
        for key, value in self._goodLetters.items():
            if key not in line:
                return False
            if key in self._correctLetters.keys() and line.count(key) < 2:
                return False
            pos = line.find(key)
            if pos in value:
                return False
        for key, value in self._correctLetters.items():
            for pos in value:
                if line[pos] != key:
                    return False
        return True

    def _win(self, lettersState):
        print(lettersState)
        if '🔳' in lettersState or '🟨' in lettersState or '⬛' in lettersState:
            return False
        return True

    def _applyWord(self, lettersState, word):
        for count in range(0, 5):
            if '🟩' == lettersState[count]:
                if word[count] in self._goodLetters.keys():
                    del self._goodLetters[word[count]]
                if word[count] not in self._correctLetters.keys():
                    self._correctLetters[word[count]] = [ count ]
                    continue
                self._correctLetters[word[count]].append(count)
            if '🟨' == lettersState[count]:
                if word[count] not in self._goodLetters.keys():
                    self._goodLetters[word[count]] = [ count ]
                    continue
                self._goodLetters[word[count]].append(count)
            if '⬛' == lettersState[count]:
                self._badLetters.append(word[count])

    def newWordle(self):
        self._controller.tryAgain()
        self._correctLetters = {}
        self._goodLetters = {}
        self._badLetters = []
        sleep(3)

    def solve(self):
        with open('words.txt', 'r') as wordsFile:
            for row in range(1,7):
                words = []
                wordsFile.seek(0)
                for line in wordsFile:
                    if self._verifyLine(line):
                        words.append(line)
                if len(words) > 1:
                    word = words[random.randint(0, len(words) - 1)]
                elif len(words) == 1:
                    word = words[0]
                self._controller.sendWord(word)
                sleep(2)
                lettersState = self._controller.getFeedback(row)
                if self._win(lettersState):
                    print("WIN: " + word, end="")
                    break
                self._applyWord(lettersState, word)

if __name__ == '__main__':
    controller = WebSiteController('https://mikhad.github.io/wordle/#infinite')
    solver = WordleSolver(controller)
    for _ in range(0, 10):
        solver.solve()
        sleep(5)
        solver.newWordle()
        print()
    controller.quit()