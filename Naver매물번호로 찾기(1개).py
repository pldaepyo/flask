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

# Selenium WebDriver 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
# User-Agent 설정
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

# WebDriver Manager를 사용하여 ChromeDriver 자동 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def scrape_listings_for_apt(apt_code):
    listings = []
    cnt = 1
    no_data_count = 0  # 데이터가 없는 페이지 수를 추적하기 위한 카운터

    while True:
        try:
            url = f"https://m.land.naver.com/complex/getComplexArticleList?hscpNo={apt_code}&cortarNo=4113110100&tradTpCd=A1:B1&order=prc&showR0=N&page={cnt}"
            driver.get(url)
            
            pre_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'pre')))
            data = json.loads(pre_element.text)
            
            if not data['result'] or not data['result']['list']:
                no_data_count += 1
                if no_data_count >= 2:  # 데이터가 연속으로 2번 없을 경우 중단
                    break
                else:
                    cnt += 1
                    continue  # 다음 페이지로 넘어가기 전에 재시도

            listings.extend(data['result']['list'])
            no_data_count = 0  # 데이터를 발견하면 카운터를 리셋
            print(f"Page {cnt} processed for Apt Code {apt_code}.")
            cnt += 1
        except Exception as e:
            print(f"Error processing page {cnt} for Apt Code {apt_code}: {e}")
            break

    return listings


# 사용자가 지정한 apt_code에 대해 매물 정보 수집
user_apt_code = '121991'  # 사용자가 지정할 apt_code
listings = scrape_listings_for_apt(user_apt_code)

# 오늘 날짜를 YYYYMMDD 형식으로 얻기
today = datetime.now().strftime("%Y%m%d")

# 파일 이름 설정 및 데이터 저장
if listings:
    # 첫 번째 매물의 'atclNm'과 오늘 날짜를 파일 이름으로 사용
    apt_name = listings[0]['atclNm'].replace("/", "_").replace("\\", "_")  # 파일 이름으로 사용 불가능한 문자 대체
    filename = f"{apt_name} {today}"
    output_file_path = f'D:\\Google 드라이브\\17. 코딩 공부\\Naver 매물\\{filename}.xlsx'
else:
    # 매물이 없는 경우 기본 파일 이름에 오늘 날짜 추가
    filename = f"{user_apt_code} {today}"
    output_file_path = f'D:\\Google 드라이브\\17. 코딩 공부\\Naver 매물\\{filename}.xlsx'

# 수집된 데이터를 DataFrame으로 변환하고 저장
listings_df = pd.DataFrame(listings)
listings_df.to_excel(output_file_path, index=False)

driver.quit()
print(f"스크래핑 완료. 파일 저장 위치: {output_file_path}")