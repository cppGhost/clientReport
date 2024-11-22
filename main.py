import requests

# ЗАПРОС НА УСТАНОВКИ
def getDataFromAppsFlyer(appName, type):

    mediaSourceCountDict = {}

    url = "https://hq1.appsflyer.com/api/raw-data/export/app/" + appName + "/" + type + "/v5?from=2024-11-13&to=2024-11-19&maximum_rows=1000000"
    headers = {
        "accept": "text/csv",
        "authorization": "Bearer eyJhbGciOiJBMjU2S1ciLCJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwidHlwIjoiSldUIiwiemlwIjoiREVGIn0.aikOWVa1dAjqKbwk-l_m07a7XclQRoG-rnrj3EhgOj7jmfz4QKLkgA.hWSGvVbjxELQJpcN.4qraCp6v3_XM9RcupS3rI1IJh0-PBs5wWJXfR2d6NqMhOiqyzGQ7LHinRUoacySti64_s5HSXpX_QRkNRUJHGL9ZupRMGhFJFmhJmpaWr8T5lBN6-oFmX9m4Xok8qTWRLIBGtHYtAgABk3MmMV7AAXWCbh_J-mOvJX48q6P1-STeMz_4GpbOVE47OM9KbBEIKu-BRV70Rqk5UorSJTHqecP3qE9Z6FNL97Zo5ASqmQsuTuC2D8TcEVugc0zXp5tuR40QskqiksexOt_Ul1au7cgPeGHCJJB-bwR2Wtekjm6KrtEIhJut76I3EZkq7LmRhCLO-0U7-uNN21oluvj1GC6q5wGxbZ1T98N9ZDA9A7hjXPTot2bYxyHOr8wfVJJb7hkbkVvZU7wR2T6VyuYNXm8KtVS_JYCDbAeiGuF6u5Z1aQx_c5HxcS59QCZH1CNhAd89Fk0_m-2M0kI50CLDICdGnYKlWDuCZhgl-YkbGAT-TchnKZWEwPjOjh5X0qkcFIeTdcXpw6e9Yw8PCYJHaE8.GJx9usdCVHAd4meyrYzBpg"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:

        # из текста делаем двумерный массив
        strings = response.text.split('\n')
        print(name + " установки всего строк: " + str(len(strings)))

        resultArray = []
        for buf in strings:
            line = buf.split(',')
            resultArray.append(line)

        # ищем колонку media source
        mediaSourceColumn = -1
        for line in resultArray:
            for i in range(len(line)):
                if line[i] == "Media Source":
                    mediaSourceColumn = i
                    break
            break

        # ищем все media source и считаем их количество
        if mediaSourceColumn != -1:
            index = 1
            while index < len(resultArray):
                line = resultArray[index]
                if mediaSourceColumn > len(line):
                    break

                mediaSource = line[mediaSourceColumn]

                if not mediaSource in mediaSourceCountDict:
                    mediaSourceCountDict[mediaSource] = 1
                else:
                    mediaSourceCountDict[mediaSource] += 1

                index += 1

        mediaSourceCountDict = dict(sorted(mediaSourceCountDict.items()))

    return mediaSourceCountDict

# список всех клиентов
appNameList = ["robot.zaimer.ru"]

installDict = []
fraudDict = []

for name in appNameList:

    installDict = getDataFromAppsFlyer(name, "installs_report")
    fraudDict = getDataFromAppsFlyer(name, "blocked_installs_report")

aaa = 5

