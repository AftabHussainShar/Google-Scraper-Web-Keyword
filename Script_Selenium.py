from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def check_keywords(url, keywords):
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))) 

        text = driver.find_element(By.TAG_NAME, 'body').text.lower()

        for keyword in keywords:
            if keyword.lower() in text:
                return "Yes"
        return "No"
    
    except Exception as e:
        return "Not accessible"
    
    finally:
        driver.quit()

def process_url(url, keywords):
    result = check_keywords(url, keywords)
    print(f"URL: {url} Result: {result}")
    return result

def process_csv(input_csv, output_csv, keywords):
    df = results
    df['Result'] = df['link'].apply(lambda x: process_url(x, keywords))
    file_exists = os.path.isfile(output_csv)
    if file_exists:
        results.to_csv(output_csv, mode='a', index=False, header=False)
    else:
        results.to_csv(output_csv, index=False)

def filter_results():
    input_csv = 'GoogleResults.csv'
    output_csv = 'GoogleResults_filtered.csv'
    keywords = ["sale", "purchase", "Texas"]

    process_csv(input_csv, output_csv, keywords)

def simpleGoogleSearch(query, start, driver):
    results = []

    query = query.replace(' ', '+')
    URL = f"https://google.com/search?q={query}"

    driver.get(URL)
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for g in soup.find_all('div', class_='yuRUbf'):
            anchors = g.find_all('a')

            if anchors:
                link = anchors[0]['href']
                title = g.find('h3').text
                item = {"title": title, "link": link}
                results.append(item)

        
        try:
            more_results_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-ved][aria-label="More results"]'))
            )
            style = more_results_button.get_attribute("style")
            if "scale(0)" in style:
                print("More results button is hidden.")
                break

            if more_results_button.is_enabled():
                driver.execute_script("arguments[0].click();", more_results_button)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'result-stats')))
            else:
                break
        except Exception as e:
            print("Error occurred:", e)
            break

    return results

def googleToPandas(googleQuery):
    resultsList = []

    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        resultsList.extend(simpleGoogleSearch(googleQuery, 0, driver))
    finally:
        driver.quit()

    return pd.DataFrame(resultsList)

googleSearchQuery = "Texas land for Buy Sale"
results = googleToPandas(googleSearchQuery)
results = results.drop_duplicates()
file_exists = os.path.isfile('GoogleResults.csv')
if file_exists:
    results.to_csv('GoogleResults.csv', mode='a', index=False, header=False)
else:
    results.to_csv('GoogleResults.csv', index=False)
filter_results()
