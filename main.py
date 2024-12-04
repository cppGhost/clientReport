import requests
import gspread
import time
from datetime import date

# КЛИЕНТ
class appskaClient:

    def __init__(self, clientName, androidID, iosID, eventName):

        self.clientName = clientName
        self.androidID = androidID
        self.iosID = iosID
        self.eventName = eventName

# ИТОГОВАЯ СТРОКА ОТЧЕТА
class rawDataExportRow:

    def __init__(self, mediaSource, platform, partner, campaignName):

        self.mediaSource = mediaSource
        self.platform = platform
        self.partner = partner
        self.campaignName = campaignName

    def __eq__(self, other):

        return (isinstance(other, type(self))
                and (self.mediaSource, self.platform, self.partner, self.campaignName) ==
                    (other.mediaSource, other.platform, other.partner, self.campaignName))

    def __hash__(self):
        return hash((self.mediaSource, self.platform, self.partner, self.campaignName))

def writeToGoogleSheet(sheet, row, column, value):

    sheet.update_cell(row, column, value)
    time.sleep(0.8)

def getDataFromAppsFlyer(appName, type, eventName=""):

    print("Поиск для " + appName + " параметр "+ type)
    mediaSourceCountDict = {}

    currentDate = date.today()
    dateFilter = "&from=" + str(currentDate.year) + "-" + "{:02}".format(currentDate.month) + "-01&to="
    dateFilter += str(currentDate.year) + "-" + "{:02}".format(currentDate.month) + "-" + "{:02}".format(currentDate.day - 1)

    #url = "https://hq1.appsflyer.com/api/raw-data/export/app/" + appName + "/" + type + "/v5?maximum_rows=1000000" + dateFilter
    url = "https://hq1.appsflyer.com/api/raw-data/export/app/" + appName + "/" + type + "/v5?maximum_rows=1000000&from=2024-11-01&to=2024-11-15"

    # для выгрузки по событиям добавляем нужны тип события
    if eventName != "":
        url += ("&event_name=" + eventName)

    headers = {
        "accept": "text/csv",
        "authorization": "Bearer eyJhbGciOiJBMjU2S1ciLCJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwidHlwIjoiSldUIiwiemlwIjoiREVGIn0.aikOWVa1dAjqKbwk-l_m07a7XclQRoG-rnrj3EhgOj7jmfz4QKLkgA.hWSGvVbjxELQJpcN.4qraCp6v3_XM9RcupS3rI1IJh0-PBs5wWJXfR2d6NqMhOiqyzGQ7LHinRUoacySti64_s5HSXpX_QRkNRUJHGL9ZupRMGhFJFmhJmpaWr8T5lBN6-oFmX9m4Xok8qTWRLIBGtHYtAgABk3MmMV7AAXWCbh_J-mOvJX48q6P1-STeMz_4GpbOVE47OM9KbBEIKu-BRV70Rqk5UorSJTHqecP3qE9Z6FNL97Zo5ASqmQsuTuC2D8TcEVugc0zXp5tuR40QskqiksexOt_Ul1au7cgPeGHCJJB-bwR2Wtekjm6KrtEIhJut76I3EZkq7LmRhCLO-0U7-uNN21oluvj1GC6q5wGxbZ1T98N9ZDA9A7hjXPTot2bYxyHOr8wfVJJb7hkbkVvZU7wR2T6VyuYNXm8KtVS_JYCDbAeiGuF6u5Z1aQx_c5HxcS59QCZH1CNhAd89Fk0_m-2M0kI50CLDICdGnYKlWDuCZhgl-YkbGAT-TchnKZWEwPjOjh5X0qkcFIeTdcXpw6e9Yw8PCYJHaE8.GJx9usdCVHAd4meyrYzBpg"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:

        # из текста делаем двумерный массив
        strings = response.text.split('\n')

        print(appName + " параметр найдено: " + str(len(strings)))

        resultArray = []
        for buf in strings:
            line = buf.split(',')
            resultArray.append(line)

        # ищем колонку media source
        mediaSourceColumn = -1
        paltformColumn = -1
        partnerColumn = -1
        campaignNameColumn = -1

        for line in resultArray:
            for i in range(len(line)):

                if line[i] == "Media Source":
                    mediaSourceColumn = i

                elif line[i] == "Platform":
                    paltformColumn = i

                elif line[i] == "Partner":
                    partnerColumn = i

                elif line[i] == "Campaign":
                    campaignNameColumn = i

            break

        # ищем все media source и считаем их количество
        if mediaSourceColumn != -1:
            index = 1
            while index < len(resultArray):
                line = resultArray[index]
                if mediaSourceColumn > len(line) or paltformColumn > len(line):
                    break

                mediaSource = line[mediaSourceColumn]
                paltform = line[paltformColumn]
                partner = line[partnerColumn]
                campaignName = line[campaignNameColumn]

                item = rawDataExportRow(mediaSource, paltform, partner, campaignName)

                if not item in mediaSourceCountDict:
                    mediaSourceCountDict[item] = 1
                else:
                    mediaSourceCountDict[item] += 1

                index += 1

    return mediaSourceCountDict

# теку

# список всех клиентов
appNameList = []
appNameList.append( appskaClient("Leon", "com.leonru.mobile5", "", "af_first_deposit") )

for name in appNameList:

    installDict = {}
    installFraudDict = {}
    eventDict = {}
    eventFraudDict = {}

    # подключаемся к таблице с клиентом с нужным месяцем
    gc = gspread.service_account('C:\\FraudAlert\\fraudalert-4cdb5f092ad5.json')

    document = gc.open_by_url("https://docs.google.com/spreadsheets/d/1gHW7mwoI7own9HauvpDGG1VscU8mz5_eWOwqBg11yXI/edit?gid=0#gid=0")
    mainSheet = document.get_worksheet( date.today().month - 1 )

    # очищаем предыдущие результаты
    mainSheet.delete_rows(9, 999)
    mainSheet.add_rows(999)

    # собираем установки, ивенты и фрод
    if name.androidID != "":

        writeToGoogleSheet(mainSheet, 1, 16, "Загрузка установок Android")
        tempDict = getDataFromAppsFlyer(name.androidID, "installs_report")
        installDict.update(tempDict)

        writeToGoogleSheet(mainSheet, 1, 16, "Загрузка фрода по установкам Android")
        tempDict = getDataFromAppsFlyer(name.androidID, "detection")
        installFraudDict.update(tempDict)

        writeToGoogleSheet(mainSheet, 1, 16, "Загрузка событий Android")
        tempDict = getDataFromAppsFlyer(name.androidID, "in_app_events_report", name.eventName)
        eventDict.update(tempDict)

        writeToGoogleSheet(mainSheet, 1, 16, "Загрузка фрода по событиям Android")
        tempDict = getDataFromAppsFlyer(name.androidID, "fraud-post-inapps", name.eventName)
        eventFraudDict.update(tempDict)

    if name.iosID != "":
        writeToGoogleSheet(mainSheet, 1, 16, "Загрузка установок IOS")
        tempDict = getDataFromAppsFlyer(name.iosID, "installs_report")
        installDict.update(tempDict)

        writeToGoogleSheet(mainSheet, 1, 16, "Загрузка фрода по установкам IOS")
        tempDict = getDataFromAppsFlyer(name.iosID, "detection")
        installFraudDict.update(tempDict)

        writeToGoogleSheet(mainSheet, 1, 16, "Загрузка событий IOS")
        tempDict = getDataFromAppsFlyer(name.iosID, "in_app_events_report", name.eventName)
        eventDict.update(tempDict)

        writeToGoogleSheet(mainSheet, 1, 16, "Загрузка фрода по событиям IOS")
        tempDict = getDataFromAppsFlyer(name.iosID, "fraud-post-inapps", name.eventName)
        eventFraudDict.update(tempDict)

    # записываем результаты в таблицу
    reportList = []
    writeToGoogleSheet(mainSheet, 1, 16, "Вывод результатов")

    for item in installDict.keys():

        installValue = installDict[item]

        fraudValue = 0
        if item in installFraudDict:
            fraudValue = installFraudDict[item]

        eventValue = 0
        if item in eventDict:
            eventValue = eventDict[item]

        eventFraudValue = 0
        if item in eventFraudDict:
            eventFraudValue = eventFraudDict[item]

        # формируем строки для google sheet
        body = [item.platform,
                item.partner,
                item.campaignName,
                item.mediaSource,
                "",  # network
                "",  # Affiliate manager
                "",  # Status
                str(installDict[item]),
                fraudValue,
                str(round(fraudValue / installValue * 100, 1)) + "%",
                str(installValue - fraudValue),
                str(eventValue),
                str(eventFraudValue),
                str(round(eventFraudValue / eventValue * 100, 1) if eventValue else 0) + "%",
                str(eventValue - eventFraudValue)]

        reportList.append(body)

    # готовим диапазон для обновления
    if len(reportList) > 0:

        bodyMaxLen = len(reportList[0])

        # range для строки
        end_col = chr(ord('A') + bodyMaxLen - 1)
        cell_range = f'A{9}:{end_col}{9+len(reportList)-1}'
        cell_list = mainSheet.range(cell_range)

        for i, cell in enumerate(cell_list):
            cell.value = reportList[int(i / bodyMaxLen)][i % bodyMaxLen]

        # обновляем сразу всю строку
        mainSheet.update_cells(cell_list)

    writeToGoogleSheet(mainSheet, 1, 16, "ГОТОВО")

