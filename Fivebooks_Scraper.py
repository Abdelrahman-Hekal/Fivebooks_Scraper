from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService 
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import pandas as pd
import time
import unidecode
import csv
import sys
import numpy as np

def initialize_bot():

    # Setting up chrome driver for the bot
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # installing the chrome driver
    driver_path = ChromeDriverManager().install()
    chrome_service = ChromeService(driver_path)
    # configuring the driver
    driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    ver = int(driver.capabilities['chrome']['chromedriverVersion'].split('.')[0])
    driver.quit()
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.page_load_strategy = 'normal'
    chrome_options.add_argument("--disable-notifications")
    # disable location prompts & disable images loading
    prefs = {"profile.default_content_setting_values.geolocation": 2, "profile.managed_default_content_settings.images": 2, "profile.default_content_setting_values.cookies": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = uc.Chrome(version_main = ver, options=chrome_options) 
    driver.set_window_size(1920, 1080)
    driver.maximize_window()
    driver.set_page_load_timeout(300)

    return driver


def scrape_fivebooks():

    start = time.time()
    print('-'*75)
    print('Scraping fivebooks.com ...')
    print('-'*75)
    # initialize the web driver
    driver = initialize_bot()
    driver2 = initialize_bot()

    # initializing the dataframe
    data = pd.DataFrame()

    # scraping books urls
    homepages = ['https://fivebooks.com/category/business/leadership/', 'https://fivebooks.com/category/mathematics-and-science/popular-science/', 'https://fivebooks.com/category/health-and-lifestyle/family-relationships/', 'https://fivebooks.com/category/health-and-lifestyle/happiness/', 'https://fivebooks.com/category/history/american-history/', 'https://fivebooks.com/category/history/ancient-history/', 'https://fivebooks.com/category/history/modern-history/', 'https://fivebooks.com/category/history/history-of-science/', 'https://fivebooks.com/category/history/historical-figures/', 'https://fivebooks.com/category/history/military-history/', 'https://fivebooks.com/category/biography/', 'https://fivebooks.com/category/nonfiction-books/essays/', 'https://fivebooks.com/category/biography/memoir/', 'https://fivebooks.com/category/biography/artist-biographies/', 'https://fivebooks.com/category/nonfiction-books/travel-books/', 'https://fivebooks.com/category/nonfiction-books/true-crime/', 'https://fivebooks.com/category/politics-and-society/feminism/', 'https://fivebooks.com/category/psychology/mental-health/', 'https://fivebooks.com/category/psychology/self-help/', 'https://fivebooks.com/category/fiction/classic-english-literature/', 'https://fivebooks.com/category/fiction/world-literature-books/', 'https://fivebooks.com/category/fiction/literary-criticism/', 'https://fivebooks.com/category/fiction/literary-figures/', 'https://fivebooks.com/category/fiction/contemporary-fiction/', 'https://fivebooks.com/category/fiction/poetry/', 'https://fivebooks.com/category/biography/memoir/', 'https://fivebooks.com/category/fiction/comics-graphic-novels/', 'https://fivebooks.com/category/fiction/fairy-tales-mythology/', 'https://fivebooks.com/category/fiction/historical-fiction/', 'https://fivebooks.com/category/fiction/horror-books/', 'https://fivebooks.com/category/fiction/humour/', 'https://fivebooks.com/category/fiction/crime-books/', 'https://fivebooks.com/category/fiction/science-fiction/', 'https://fivebooks.com/category/fiction/short-stories/', 'https://fivebooks.com/category/fiction/romance/', 'https://fivebooks.com/category/fiction/thriller-books/', 'https://fivebooks.com/category/fiction/mystery-books/', 'https://fivebooks.com/category/fiction/fantasy/']
 
    nbooks = 0
    for homepage in homepages:

        driver.get(homepage)
        # handling lazy loading
        while True:
            try:
                height1 = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script(f"window.scrollTo(0, {height1})")
                time.sleep(5)
                height2 = driver.execute_script("return document.body.scrollHeight")
                if int(height2) == int(height1):
                    break
            except Exception as err:
                continue

        # scraping books details
        print('-'*75)
        print('Scraping Books Info...')
        try:
            sections = wait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "section[class='book-list dynamic-bookshelf']")))
        except:
            continue
        for sec in sections:
            try:
                books = wait(sec, 5).until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))
                header = wait(sec, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).get_attribute('textContent')
                if 'recommended by' in header:
                    subj = header.split(',')[0].strip()
                    rcmnd = header.split(',')[1].replace('recommended by', '').strip()
                else:
                    subj = header
                    rcmnd = ''

                title_link = ''
                try:
                    header = wait(sec, 2).until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
                    title_link = wait(header, 2).until(EC.presence_of_element_located((By.TAG_NAME, "a"))).get_attribute('href')
                except:
                    pass

                for book in books:
                    try:      
                        details = {}
                        nbooks += 1
                        print(f'Scraping the info for book {nbooks}')

                        title, author = '', ''
                        try:
                            h2 = wait(book, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2[class='book-title -listbook']"))).get_attribute('textContent')
                            title = h2.split('\n')[0].strip()
                            author = h2.split('\n')[1].replace(' by ', '').strip()
                        except:
                            pass

                        details['Title'] = title
                        details['Title Link'] = title_link
                        details['Author'] = author

                        cat, subcat = '', ''
                        try:
                            elems = homepage.split('/')
                            for i, elem in enumerate(elems):
                                if elem == 'category':
                                    cat = elems[i+1].replace('-', ' ').title()
                                    subcat = elems[i+2].replace('-', ' ').title()
                                    break
                        except:
                            pass

                        details['Category'] = cat
                        details['Subcategory'] = subcat
                        details['Subject'] = subj
                        details['Recommended by'] = rcmnd

                        # Amazon Link
                        Amazon = ''
                        try:
                            url = wait(book, 2).until(EC.presence_of_element_located((By.TAG_NAME, "a"))).get_attribute('href')
                            driver2.get(url)
                            url = driver2.current_url
                            if 'amazon.com' in url:
                                Amazon = url
                        except:
                            pass          
                
                        details['Amazon Link'] = Amazon
            
                        # appending the output to the datafame            
                        data = data.append([details.copy()])
                        # saving data to csv file each 100 links
                        if np.mod(nbooks, 100) == 0:
                            print('Outputting scraped data to Excel sheet ...')
                            data.to_excel('FiveBooks_data.xlsx', index=False)
                    except:
                        pass
            except:
                pass

    # optional output to Excel
    data.to_excel('FiveBooks_data.xlsx', index=False)
    elapsed = round((time.time() - start)/60, 2)
    print('-'*75)
    print(f'fivebooks.com scraping process completed successfully! Elapsed time {elapsed} mins')
    print('-'*75)
    driver.quit()
    driver2.quit()

    return data

if __name__ == "__main__":
    
    data = scrape_fivebooks()

