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
import os
import threading

# Selenium WebDriver 설정
def setup_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def scrape_listings_for_dong(driver, dong_code):
    listings = []
    cnt = 1
    while True:
        try:
            url = f"https://m.land.naver.com/cluster/ajax/articleList?rletTpCd=APT%3AABYG&tradTpCd=A1%3AB1&spcMin=66&spcMax=165&tag=MIDFLOOR%3AHSEH100&cortarNo={dong_code}&page={cnt}"
            driver.get(url)
            
            pre_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'pre')))
            data = json.loads(pre_element.text)
            
            if not data['body']:
                break  # 페이지에 데이터가 없으면 중단
            
            listings.extend(data['body'])
            cnt += 1
        except Exception as e:
            break

    return listings

def scrape_and_save(dong_code_entry, result_label):
    dong_code = dong_code_entry.get()
    if not dong_code:
        messagebox.showinfo("입력 오류", "동 코드를 입력해주세요.")
        return

    driver = setup_driver()
    listings = scrape_listings_for_dong(driver, dong_code)
    if listings:
        listings_df = pd.DataFrame(listings)
        output_file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if output_file_path:
            listings_df.to_excel(output_file_path, index=False)
            result_label.config(text="스크래핑 완료!")
        else:
            result_label.config(text="파일 저장이 취소되었습니다.")
    else:
        result_label.config(text="데이터가 없습니다.")
    driver.quit()

def scrape_gui():
    root = tk.Tk()
    root.title("Naver Land Scraper")

    tk.Label(root, text="동 코드:").pack(padx=10, pady=5)
    dong_code_entry = tk.Entry(root)
    dong_code_entry.pack(padx=10, pady=5)

    result_label = tk.Label(root, text="")
    result_label.pack(padx=10, pady=10)

    scrape_button = tk.Button(root, text="스크래핑 시작", command=lambda: threading.Thread(target=scrape_and_save, args=(dong_code_entry, result_label,)).start())
    scrape_button.pack(padx=10, pady=5)

    root.mainloop()

# GUI 실행
if __name__ == "__main__":
    scrape_gui()