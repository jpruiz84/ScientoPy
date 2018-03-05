import time
import os
from selenium import webdriver
import shutil
import random
from termcolor import colored
import re
import csv
from selenium.webdriver.support.ui import Select


BASE_WOS_URL = "http://ezproxyegre.uniandes.edu.co:8888/login?url=http://apps.webofknowledge.com/"
DOWNLOAD_FOLDER = "/wosData"
SEARCH_STRING = '"Internet of things"'

RELOAD_MIN_DELAY = 15
RELOAD_MAX_DELAY = 30
LOAD_DMIN = 3
LOAD_DMAX = 5

MAX_PER_DOWNLOAD = 500

DownloadPath = ""

def startWebDriver(start_url):
  print("Starting WebDriver...")
  chrome_options = webdriver.ChromeOptions()
  prefs = {
      "download": {"default_directory": DownloadPath,
                   "directory_upgrade": True,
                   "extensions_to_open": ""},
      "switches": ["-silent", "--disable-logging"],
      "chromeOptions": {"args": ["-silent", "--disable-logging"]}
  }
  chrome_options.add_experimental_option("prefs", prefs)

  driver = webdriver.Chrome(chrome_options=chrome_options)
  driver.implicitly_wait(5)
  driver.get(start_url)
  driver.maximize_window()

  return driver

def WosLogIn(driver):
  print("Login...")

  # Log in
  user = driver.find_element_by_css_selector("#capa1 > form:nth-child(5) > font:nth-child(1) > input:nth-child(1)")
  password = driver.find_element_by_css_selector("#capa1 > form:nth-child(5) > font:nth-child(1) > input:nth-child(5)")

  user.clear()
  user.send_keys("jpruiz84")
  password.clear()
  password.send_keys("clavetaio")
  login = driver.find_element_by_css_selector("#botingre")
  login.click()


def wosDownloadList(driver, fromCount, toCount):

  try:

    # Refresh page
    driver.refresh()

    time.sleep(random.randint(LOAD_DMIN, LOAD_DMAX))

    # Select save to other file format
    select = Select(driver.find_element_by_name('saveToMenu'))
    select.select_by_value("other")

    # Click on Records
    driver.find_element_by_css_selector("#numberOfRecordsRange").click()

    # Put from and to
    fromElement = driver.find_element_by_css_selector("#markFrom")
    toElement = driver.find_element_by_css_selector("#markTo")
    fromElement.send_keys(str(fromCount))
    toElement.send_keys(str(toCount))

    # Select Save to Other File Formats
    select = Select(driver.find_element_by_name('fields_selection'))
    select.select_by_index(3)

    # Select Save tabWinUTF8
    select = Select(driver.find_element_by_id('saveOptions'))
    select.select_by_value("tabWinUTF8")

    time.sleep(1)

    # Click on send
    driver.find_element_by_xpath("//span[@class='quickoutput-action']/input[@title='Send']").click()

    print("Downloading...")

    # Wait until the download is created
    while not os.path.isfile(DownloadPath + "/savedrecs.txt.crdownload"):
      # If donwloaded very fast
      if os.path.isfile(DownloadPath + "/savedrecs.txt"):
        if (os.stat(DownloadPath + "/savedrecs.txt").st_size >= 0):
          break
      time.sleep(1)

    # Wait until download is finished
    while os.path.isfile(DownloadPath + "/savedrecs.txt.crdownload"):
      time.sleep(1)

    # Wait for file to be renamed by chrome
    time.sleep(2)

    if(os.stat(DownloadPath + "/savedrecs.txt").st_size == 0):
      print("Error, bad file size")
      return False

    print("Download finished.")

    # Click on close
    driver.find_element_by_xpath('//*[ @ id = "ui-id-7"]/form/div[2]/a').click()
    return True


  except:
    return False


# Start main program ********************************************

print("Get data from WoS")

DownloadPath = os.getcwd() + DOWNLOAD_FOLDER

print("Download path: %s" % DownloadPath)

if not os.path.exists(DownloadPath):
  print("No download folder, creating")
  os.makedirs(DownloadPath)

# Remove all files from download folder
shutil.rmtree(DownloadPath)

# Start CSV to store results
ofile = open("getWosResults.csv", 'w')
fieldnames = ["Number", "from", "to", "Papers", "Time"]
writer = csv.DictWriter(ofile, fieldnames=fieldnames, dialect=csv.excel_tab)
writer.writeheader()

# Log in to WoS
driver = startWebDriver(BASE_WOS_URL)
WosLogIn(driver)
time.sleep(random.randint(LOAD_DMIN, LOAD_DMAX))

# Put the search string
searchField = driver.find_element_by_css_selector("#value\(input1\)")
searchField.clear()
searchField.send_keys(SEARCH_STRING)
searchButton = driver.find_element_by_css_selector("#WOS_GeneralSearch_input_form_sb")
searchButton.click()
time.sleep(random.randint(LOAD_DMIN, LOAD_DMAX))

# Find the total papers
documentsCount = driver.find_element_by_css_selector("#hitCount\.top").text
if re.findall("\d+", documentsCount.replace(",", "")) == []:
  totalPapersToFind = 0
else:
  totalPapersToFind = int(re.findall("\d+", documentsCount.replace(",", ""))[0])
print("totalPapersToFind: " + str(totalPapersToFind))

papersCount = 0
countDonwloads = 0
fromCount = 1
startTime = time.time()
while True:
  # Update toCount
  if(fromCount + MAX_PER_DOWNLOAD) <= totalPapersToFind:
    resultsPerDownload = MAX_PER_DOWNLOAD
  else:
    resultsPerDownload = totalPapersToFind - fromCount + 1
  toCount = fromCount + resultsPerDownload - 1

  print("Download from: %d, to: %d" %(fromCount, toCount))

  # Download and check download
  if(wosDownloadList(driver, fromCount, toCount) == False):
    reloadDelay = random.randint(RELOAD_MIN_DELAY, RELOAD_MAX_DELAY)
    print colored("Error to load, wait (seg): " + str(reloadDelay), 'red')
    time.sleep(reloadDelay)
    continue


  countDonwloads += 1
  dataWrite = {}
  dataWrite["Number"] = str(countDonwloads)
  dataWrite["from"] = fromCount
  dataWrite["to"] = toCount
  dataWrite["Papers"] = resultsPerDownload
  dataWrite["Time"] = int(time.time() - startTime)
  writer.writerow(dataWrite)

  dataWrite = {}
  papersCount +=  resultsPerDownload
  print("results found: " + str(resultsPerDownload))
  print("TOTAL papersCount: " + str(papersCount) +  ", from: " + str(totalPapersToFind))

  number = "wos_%03d-%06d" % (countDonwloads, papersCount)
  os.rename(DownloadPath + "/savedrecs.txt",
            DownloadPath + "/{0}.csv".format(number))

  if(papersCount >= totalPapersToFind):
    break

  # Update fromCount
  fromCount = toCount + 1

ofile.close()

#driver.close()


