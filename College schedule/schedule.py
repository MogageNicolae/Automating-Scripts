from __future__ import print_function

import os.path
from pprint import pprint
from time import sleep

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def createEvent(event):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('calendar', 'v3', credentials=creds)
            event = service.events().insert(calendarId='c_qt7e9qnklatkkra62l44rle7nc@group.calendar.google.com', body=event).execute()
        except HttpError as error:
            print('An error occurred: %s' % error)

class SchedulerFormatter:
    def __init__(self, siteToOpen) -> None:
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options = uc.ChromeOptions()
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--load-extension=./adblock')

        self._driver = uc.Chrome(user_data_dir='F:\Proiecte\Proiecte_py\Scripts\profile', options=chrome_options)
        self._driver.maximize_window()
        self._driver.get(siteToOpen)

    def run(self):
        sleep(2)
        rows = self._driver.find_elements(By.XPATH, '/html/body/center/table[4]/tbody/tr')

        for count in range(1, len(rows)):
            collumnsValues = rows[count].find_elements(By.XPATH, 'td')
            if collumnsValues[4].text == '224/1':
                continue
            frequency = {
                'sapt. 1': 'RRULE:FREQ=WEEKLY;INTERVAL=2;UNTIL=20230120T230000Z',
                'sapt. 2': 'RRULE:FREQ=WEEKLY;INTERVAL=2;UNTIL=20230120T230000Z',
                ' ': 'RRULE:FREQ=WEEKLY;UNTIL=20230120T230000Z',
            }
            dates = {
                ' ': {
                'Luni': '2022-10-03',
                'Marti': '2022-10-04',
                'Miercuri': '2022-10-05',
                'Joi': '2022-10-06',
                'Vineri': '2022-10-07',
                },
                'sapt. 1': {
                'Luni': '2022-10-03',
                'Marti': '2022-10-04',
                'Miercuri': '2022-10-05',
                'Joi': '2022-10-06',
                'Vineri': '2022-10-07',
                },
                'sapt. 2': {
                'Luni': '2022-10-10',
                'Marti': '2022-10-11',
                'Miercuri': '2022-10-12',
                'Joi': '2022-10-13',
                'Vineri': '2022-10-14',
                }
            }
            event = {
                'summary': collumnsValues[5].text[0] + '-' + collumnsValues[3].text + '  ' + collumnsValues[6].text,
                'description': collumnsValues[7].text,
                'start': {
                    'dateTime': dates[collumnsValues[2].text][collumnsValues[0].text] + 'T' + collumnsValues[1].text.split('-')[0].replace('.', ':') + ':00:00',
                    'timeZone': 'Europe/Bucharest',
                },
                'end': {
                    'dateTime': dates[collumnsValues[2].text][collumnsValues[0].text] + 'T' + collumnsValues[1].text.split('-')[1].replace('.', ':') + ':00:00',
                    'timeZone': 'Europe/Bucharest',
                },
                'recurrence': [
                    frequency[collumnsValues[2].text],
                ],
                'reminders': {
                    'useDefault': True,
                },
            }
            pprint(event)
            createEvent(event)
        self._driver.quit()

if __name__ == '__main__':
    schedule = SchedulerFormatter('https://www.cs.ubbcluj.ro/files/orar/2022-1/tabelar/I2.html')
    schedule.run()
    