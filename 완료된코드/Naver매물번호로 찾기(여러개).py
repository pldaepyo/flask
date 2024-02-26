import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import json
import os
import time

def scrape_listings_for_apt(apt_code):
    listings = []
    cnt = 1
    no_data_count = 0

    while True:
        try:
            url = f"https://m.land.naver.com/complex/getComplexArticleList?hscpNo={apt_code}&cortarNo=4113110100&tradTpCd=A1:B1&order=prc&showR0=N&page={cnt}"
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

    return listings

def save_listings_to_excel(listings, apt_code):
    today = datetime.now().strftime("%Y%m%d")
    if listings:
        apt_name = listings[0]['atclNm'].replace("/", "_").replace("\\", "_")
        filename = f"{apt_name} {today}"
    else:
        filename = f"{apt_code} {today}"
    output_file_path = f'D:\\Google 드라이브\\17. 코딩 공부\\Naver 매물\\{filename}.xlsx'
    listings_df = pd.DataFrame(listings)
    listings_df.to_excel(output_file_path, index=False)
    print(f"스크래핑 완료. 파일 저장 위치: {output_file_path}")

# Selenium WebDriver 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 사용자가 지정할 여러 apt_code
apt_codes = ['121991', '19451', '25960', '22290', '19358', '22065', '23771', '23768', '112392', '9810']  # 예시 코드 리스트

for apt_code in apt_codes:
    listings = scrape_listings_for_apt(apt_code)
    save_listings_to_excel(listings, apt_code)

driver.quit()
