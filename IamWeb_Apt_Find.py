from flask import Flask, request, jsonify
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

app = Flask(__name__)

def scrape_listings_for_apt(apt_code):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    listings = []
    cnt = 1
    no_data_count = 0

    while True:
        try:
            url = f"https://m.land.naver.com/complex/getComplexArticleList?hscpNo={apt_code}&cortarNo=4113110100&tradTpCd=A1&order=prc&showR0=N&page={cnt}"
            driver.get(url)
            
            pre_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'pre')))
            data = json.loads(pre_element.text)
            
            if not data['result'] or not data['result']['list']:
                no_data_count += 1
                if no_data_count >= 2:
                    break
                else:
                    cnt += 1
                    continue

            listings.extend(data['result']['list'])
            no_data_count = 0
            print(f"Page {cnt} processed for Apt Code {apt_code}.")
            cnt += 1
        except Exception as e:
            print(f"Error processing page {cnt} for Apt Code {apt_code}: {e}")
            break

    driver.quit()
    return listings

@app.route('/get_listings', methods=['POST'])
def get_listings():
    apt_code = request.json['apt_code']
    listings = scrape_listings_for_apt(apt_code)
    return jsonify(listings)

if __name__ == '__main__':
    app.run(debug=True)