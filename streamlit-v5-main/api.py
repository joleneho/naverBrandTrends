import requests
import json
from datetime import datetime

class API:
    def __init__(self, clientID='', clientSecret=''):
        self.endPoint = 'https://openapi.naver.com/v1/datalab/search'
        self.timeUnit = 'week'
        self.device = ''
        self.gender = ''
        self.ages = []
        self.keywordGroups = []
        self.clientID = clientID
        self.clientSecret = clientSecret

    def setCredential(self, clientID, clientSecret):
        self.clientID = clientID
        self.clientSecret = clientSecret

    def setStartDate(self, start):
        date = datetime.strptime(start, '%Y-%m-%d')

        if date < datetime(2016, 1, 1):
            raise Exception('Please specify a start date after January 1, 2016.')

        self.startDate = date.strftime('%Y-%m-%d')

    def setEndDate(self, end):
        self.endDate = datetime.strptime(end, '%Y-%m-%d').strftime('%Y-%m-%d')

    def setTimeUnit(self, unit):
        units = ['date', 'week', 'month']

        if unit not in units:
            raise Exception('Please specify the time unit as date, week, or month.')

        self.timeUnit = unit

    def setDevice(self, device):
        devices = ['pc', 'mo', '']

        if device and device not in devices:
            raise Exception('Please specify the device as pc or mo.')

        self.device = device

    def setGender(self, gender):
        genders = ['m', 'f', '']

        if gender and gender not in genders:
            raise Exception('Please specify the gender as m or f.')

        self.gender = gender

    def setAges(self, ages):
        """
        1: 0∼12세
        2: 13∼18세
        3: 19∼24세
        4: 25∼29세
        5: 30∼34세
        6: 35∼39세
        7: 40∼44세
        8: 45∼49세
        9: 50∼54세
        10: 55∼59세
        11: 60세 이상
        """
        if not isinstance(ages, list):
            ages = list(map(str.strip, ages.split(',')))

        self.ages = ages

    def setKeywordGroups(self, groupName, keywords):
        if not groupName or not keywords:
            raise Exception('Please specify the topic and search keyword group.')

        if not isinstance(groupName, list):
            groupName = list(map(str.strip, groupName.split(',')))

        if not isinstance(keywords, list):
            keywords = list(map(str.strip, keywords.split('/')))
        else:
            if not any(isinstance(k, list) for k in keywords):
                keywords = [keywords]
        
        for cnt, _ in enumerate(keywords):
            if not isinstance(keywords[cnt], list):
                keywords[cnt] = list(map(str.strip, keywords[cnt].split(',')))
        
        for group, keyword in zip(groupName, keywords):
            self.keywordGroups.append({
                'groupName': group,
                'keywords': keyword
            })
            # print({
            #     'groupName': group,
            #     'keywords': keyword
            # })
    def sendRequest(self):
        headers = {
            "X-Naver-Client-Id": self.clientID,
            "X-Naver-Client-Secret": self.clientSecret,
            "Content-Type": "application/json"
        }

        # print(self.keywordGroups)

        params = {
            'startDate': self.startDate,
            'endDate': self.endDate,
            'timeUnit': self.timeUnit,
            'keywordGroups': self.keywordGroups,
            'device': self.device,
            'gender': self.gender,
            'ages': self.ages
        }

        response = requests.post(self.endPoint, headers=headers, data=json.dumps(params))
        response.raise_for_status()

        return response.json()
