import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import os
import time

# Selenium WebDriver 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
# User-Agent 설정
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

# WebDriver Manager를 사용하여 ChromeDriver 자동 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def scrape_listings_for_dong(dong_code):
    listings = []
    cnt = 1
    while True:
        try:
            url = f"https://m.land.naver.com/cluster/ajax/articleList?rletTpCd=APT%3AABYG&tradTpCd=A1%3AB1&spcMin=66&spcMax=165&tag=MIDFLOOR%3AHSEH100&cortarNo={dong_code}&page={cnt}"
            driver.get(url)
            
            pre_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'pre')))
            data = json.loads(pre_element.text)
            body = data['body']
            
            if not data['body']:
                break  # 페이지에 데이터가 없으면 중단
            
            listings.extend(data['body'])
            print(f"Page {cnt} processed for Dong Code {dong_code}.")
            cnt += 1
        except Exception as e:
            print(f"Error processing page {cnt} for Dong Code {dong_code}: {e}")
            break

    return listings

# 사용자가 지정한 dong_code에 대해 매물 정보 수집
user_dong_code = input("동 코드를 입력해주세요: ") # 예 '1123010700' 사용자가 지정할 dong_code
listings = scrape_listings_for_dong(user_dong_code)

# 수집된 데이터를 DataFrame으로 변환하고 저장
listings_df = pd.DataFrame(listings)
output_file_path = input("저장할 파일 경로와 이름을 입력해주세요 (예: C:\\Users\\username\\Documents\\output.xlsx): ")

# 파일 경로에서 디렉토리 경로 추출
directory = os.path.dirname(output_file_path)

# 디렉토리가 존재하지 않는 경우 생성
if not os.path.exists(directory):
    os.makedirs(directory, exist_ok=True)

# output_file_path = f'D:\\Google 드라이브\\17. 코딩 공부\\Naver 매물\\{user_dong_code}.xlsx'
listings_df.to_excel(output_file_path, index=False)

driver.quit()
print("스크래핑 완료.")