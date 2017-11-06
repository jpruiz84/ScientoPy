import paperUtils
import time
import os
from selenium import webdriver
import shutil
import random
from termcolor import colored

BASE_SCOPUS_URL = "https://www-scopus-com.ezproxyegre.uniandes.edu.co:8843"
DOWNLOAD_FOLDER = "/home/jpruiz84/scopusData"
DATAIN_FOLDER = "./idsData/"

SAVE_FILE_DELAY = 1
RELOAD_MIN_DELAY = 15
RELOAD_MAX_DELAY = 30
PAPERS_INTERVAL_TO_DELAY = 10
LOAD_DMIN = 3
LOAD_DMAX = 5


def startWebDriver(start_url):
  print("Starting WebDriver...")

  fp = webdriver.FirefoxProfile()

  fp.set_preference("browser.download.folderList",2)
  fp.set_preference("browser.download.manager.showWhenStarting",False)
  fp.set_preference("browser.download.dir", DOWNLOAD_FOLDER)
  fp.set_preference("browser.helperApps.neverAsk.saveToDisk","text/csv")

  driver = webdriver.Firefox(firefox_profile=fp)
  driver.set_page_load_timeout(30)
  driver.get(start_url)
  driver.maximize_window()
  driver.implicitly_wait(20)

  return driver

def scopusLogIn(driver):
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

def scopusGetFirstCsv(driver, in_url):
  get_url = in_url.replace("https://www.scopus.com", "https://www-scopus-com.ezproxyegre.uniandes.edu.co:8843")

  print("Getting first CSV from: " + get_url.split("eid=")[1].split("&")[0])

  while True:
    print("Loading page...")
    driver.get(get_url)

    try:
      # Export to cvs
      time.sleep(7)
      driver.find_element_by_css_selector("#export_results").click()


      # CSV (Excel)
      time.sleep(7)
      driver.find_element_by_css_selector("li.radio-inline:nth-child(4) > label:nth-child(2)").click()
      # Bibliographical information
      biographical = driver.find_element_by_css_selector("#exportCheckboxHeaders > th:nth-child(2) > span:nth-child(1) > label:nth-child(2)")
      biographical.click()
      # Abstract and Keywords
      abstract = driver.find_element_by_css_selector("#exportCheckboxHeaders > th:nth-child(3) > span:nth-child(1) > label:nth-child(2)")
      abstract.click()
      # Export button
      driver.find_element_by_css_selector("#exportTrigger").click()

      break

    except:
      reloadDelay = random.randint(RELOAD_MIN_DELAY, RELOAD_MAX_DELAY)
      print colored("Error to load, wait (seg): " + str(reloadDelay), 'red')
      time.sleep(reloadDelay)
      continue


  # Wait until file is created
  while not os.path.isfile(DOWNLOAD_FOLDER + "/scopus.csv"):
    time.sleep(SAVE_FILE_DELAY)


def scopusGetCsv(driver, in_url):
  get_url = in_url.replace("https://www.scopus.com", "https://www-scopus-com.ezproxyegre.uniandes.edu.co:8843")

  print("Getting CSV from: " + get_url.split("eid=")[1].split("&")[0])

  while True:
    print("Loading page...")
    driver.get(get_url)


    try:
      # Export to cvs
      time.sleep(random.randint(LOAD_DMAX, LOAD_DMAX))
      driver.find_element_by_css_selector("#export_results").click()

      # Export button
      time.sleep(random.randint(LOAD_DMAX, LOAD_DMAX))
      driver.find_element_by_css_selector("#exportTrigger").click()

      break

    except:
      reloadDelay = random.randint(RELOAD_MIN_DELAY, RELOAD_MAX_DELAY)
      print colored("Error to load, wait (seg): " + str(reloadDelay), 'red')
      time.sleep(reloadDelay)
      continue


  # Wait until file is created
  while not os.path.isfile(DOWNLOAD_FOLDER + "/scopus.csv"):
    time.sleep(SAVE_FILE_DELAY)


print("Get CSV from Scopus")

papersDict = []
# Read files in the DATAIN_FOLDER
for file in os.listdir(DATAIN_FOLDER):
  if file.endswith(".csv") or file.endswith(".txt"):
    print("Reading file: %s" % (DATAIN_FOLDER + file))
    ifile = open(DATAIN_FOLDER + file, "rb")
    paperUtils.getPapersLinkFromFile(ifile, papersDict)

totalPapers = len(papersDict)
print("Total papers to read: " + str(totalPapers))


driver = startWebDriver(BASE_SCOPUS_URL)
scopusLogIn(driver)

# Remove all files from download folder
try:
  shutil.rmtree(DOWNLOAD_FOLDER)
except:
  print("No donwload folder")

count = 1
startTime = time.time()
for paper in papersDict:

  startPaperTime = time.time()
  url1 = paper["Link"]

  print("")
  print("Reading paper: {0}, from: {1}, {2}%".format(str(count), str(totalPapers),
                                                     str(100 * count / totalPapers)))
  if count == 1:
    scopusGetFirstCsv(driver, url1)
  else:
    scopusGetCsv(driver, url1)

  number = "%06d_" % (count,)
  os.rename(DOWNLOAD_FOLDER + "/scopus.csv",
            "/home/jpruiz84/scopusData/{0}.csv".format(number + url1.split("eid=")[1].split("&")[0]))

  if((count % PAPERS_INTERVAL_TO_DELAY) == 0):
    reloadDelay = random.randint(RELOAD_MIN_DELAY, RELOAD_MAX_DELAY)
    print colored("Papers interval delay (seg): " + str(reloadDelay), 'yellow')
    time.sleep(reloadDelay)

  time.sleep(random.randint(LOAD_DMAX, LOAD_DMAX))

  aveTimePerPaper = (time.time()-startTime)/count
  print("Paper time: %d s, average %d s" % (time.time()-startPaperTime, aveTimePerPaper))


  count += 1

#driver.close()