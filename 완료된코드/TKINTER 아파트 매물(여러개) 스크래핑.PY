import sys  #유효기간을 넣기 위한 라이브러리
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
from datetime import datetime #유효기간을 넣기 위한 라이브러리
import threading

# 유효기간 검사 함수
def check_expiry_date():
    expiry_date = datetime(2024, 3, 25)
    current_date = datetime.now()
    if current_date > expiry_date:
        messagebox.showinfo("만료 알림", "이 프로그램의 사용 기한이 만료되었습니다.")
        sys.exit()

# Selenium WebDriver 설정 함수
def setup_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# 스크래핑 함수
def scrape_listings_for_apt(driver, apt_code):
    listings = []
    cnt = 1
    no_data_count = 0
    while True:
        try:
            url = f"https://m.land.naver.com/complex/getComplexArticleList?hscpNo={apt_code}&tradTpCd=A1:B1&order=prc&showR0=N&page={cnt}"
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

# 스크래핑 및 파일 저장 함수
def scrape_and_save(apt_codes, save_directory):
    driver = setup_driver()
    for apt_code in apt_codes:
        listings = scrape_listings_for_apt(driver, apt_code.strip())
        if listings:
            today = datetime.now().strftime("%Y%m%d")
            apt_name = listings[0]['atclNm'].replace("/", "_").replace("\\", "_")
            filename = f"{apt_name} {today}.xlsx"
            output_file_path = f"{save_directory}/{filename}"
            listings_df = pd.DataFrame(listings)
            listings_df.to_excel(output_file_path, index=False)
            print(f"스크래핑 완료. 파일 저장 위치: {output_file_path}")
        else:
            print(f"{apt_code}에 대한 데이터가 없습니다.")
    driver.quit()
    messagebox.showinfo("성공", "모든 스크래핑 완료 및 파일 저장 성공!")

# 아파트 코드 입력 및 저장 폴더 선택 GUI
def input_and_save_gui():
    check_expiry_date()  # 프로그램 시작 시 유효기간 검사
    root = tk.Tk()
    root.title("Naver Apartment Scraper")
    def on_scrape_start():
        apt_codes_str = simpledialog.askstring("아파트 코드 입력", "아파트 코드를 콤마(,)로 구분하여 입력하세요:")
        if apt_codes_str:
            apt_codes = apt_codes_str.split(',')
            save_directory = filedialog.askdirectory(title="저장할 폴더를 선택하세요")
            if save_directory:
                threading.Thread(target=scrape_and_save, args=(apt_codes, save_directory,)).start()
            else:
                messagebox.showinfo("취소", "저장 폴더 선택이 취소되었습니다.")
        else:
            messagebox.showinfo("입력 오류", "아파트 코드를 입력해주세요.")
    tk.Button(root, text="아파트 코드 입력 및 스크래핑 시작", command=on_scrape_start).pack(padx=10, pady=10)
    root.mainloop()

if __name__ == "__main__":
    input_and_save_gui()
