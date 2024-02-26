import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
from datetime import datetime
import threading

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
    no_data_count = 0  # 데이터가 없는 페이지 수를 추적하기 위한 카운터

    while True:
        try:
            url = f"https://m.land.naver.com/complex/getComplexArticleList?hscpNo={apt_code}&tradTpCd=A1:B1&order=prc&showR0=N&page={cnt}"
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

# 스크래핑 및 파일 저장 함수
def scrape_and_save(apt_code_entry):
    apt_code = apt_code_entry.get()
    if not apt_code:
        messagebox.showinfo("입력 오류", "아파트 코드를 입력해주세요.")
        return

    driver = setup_driver()
    listings = scrape_listings_for_apt(driver, apt_code)
    driver.quit()

    if listings:
        today = datetime.now().strftime("%Y%m%d")
        apt_name = listings[0]['atclNm'].replace("/", "_").replace("\\", "_")
        filename = f"{apt_name} {today}"
    else:
        filename = f"{apt_code} {today}"
    
    output_file_path = filedialog.asksaveasfilename(
        initialdir="/",
        title="Save as",
        filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")),
        defaultextension=".xlsx",
        initialfile=filename
    )
    
    if output_file_path:
        listings_df = pd.DataFrame(listings)
        listings_df.to_excel(output_file_path, index=False)
        messagebox.showinfo("성공", "스크래핑 완료 및 파일 저장 성공!")
    else:
        messagebox.showinfo("취소", "파일 저장이 취소되었습니다.")

# GUI 설정
def scrape_gui():
    root = tk.Tk()
    root.title("Naver Apartment Scraper")

    tk.Label(root, text="아파트 코드:").pack(padx=10, pady=5)
    apt_code_entry = tk.Entry(root)
    apt_code_entry.pack(padx=10, pady=5)

    scrape_button = tk.Button(root, text="스크래핑 시작", command=lambda: threading.Thread(target=scrape_and_save, args=(apt_code_entry,)).start())
    scrape_button.pack(padx=10, pady=5)

    root.mainloop()

# GUI 실행
if __name__ == "__main__":
    scrape_gui()