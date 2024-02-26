import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import threading
import datetime

def load_and_convert_csv(file_path):
    df = pd.read_csv(file_path)
    nested_dict = {}
    for _, row in df.iterrows():
        addr_1, addr_2, addr_3, b_code = row['ADDR_1'], row['ADDR_2'], row['ADDR_3'], row['B_CODE']
        if pd.isna(addr_3):  # Check if addr_3 is NaN
            nested_dict.setdefault(addr_1, {}).setdefault(addr_2, {})[' '] = b_code
        else:
            nested_dict.setdefault(addr_1, {}).setdefault(addr_2, {})[addr_3] = b_code
    return nested_dict

def setup_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--headless")
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
                break
            listings.extend(data['body'])
            cnt += 1
        except Exception as e:
            break
    return listings

def scrape_gui(nested_dict):
    root = tk.Tk()
    root.title("Naver Land Scraper")

    addr_1_var = tk.StringVar(root)
    addr_2_var = tk.StringVar(root)
    addr_3_var = tk.StringVar(root)

    tk.Label(root, text="지역 선택:").pack(padx=10, pady=5)
    addr_1_menu = ttk.Combobox(root, textvariable=addr_1_var, values=list(nested_dict.keys()), state="readonly")
    addr_1_menu.pack(padx=10, pady=5)
    
    addr_2_menu = ttk.Combobox(root, textvariable=addr_2_var, state="readonly")
    addr_2_menu.pack(padx=10, pady=5)
    
    addr_3_menu = ttk.Combobox(root, textvariable=addr_3_var, state="readonly")
    addr_3_menu.pack(padx=10, pady=5)
    
    def on_addr1_selected(event):
        addr_1 = addr_1_var.get()
        addr_2_keys = list(nested_dict[addr_1].keys())
        addr_2_var.set('')
        addr_2_menu['values'] = addr_2_keys
        if addr_2_keys:
            addr_2_var.set(addr_2_keys[0])
            on_addr2_selected(None)

    def on_addr2_selected(event):
        addr_1 = addr_1_var.get()
        addr_2 = addr_2_var.get()
        addr_3_keys = list(nested_dict[addr_1][addr_2].keys()) if addr_2 else []
        addr_3_var.set('')
        addr_3_menu['values'] = addr_3_keys
        if addr_3_keys:
            addr_3_var.set(addr_3_keys[0])

    def scrape_and_save():
        addr_1, addr_2, addr_3 = addr_1_var.get(), addr_2_var.get(), addr_3_var.get()
        dong_code = nested_dict[addr_1][addr_2].get(' ', next(iter(nested_dict[addr_1][addr_2].values()))) if not addr_3 or addr_3 == 'NaN' else nested_dict[addr_1][addr_2][addr_3]
        driver = setup_driver()
        listings = scrape_listings_for_dong(driver, dong_code)
        driver.quit()
        if listings:
            listings_df = pd.DataFrame(listings)
            today = datetime.datetime.now().strftime("%Y%m%d")
            filename = f"{addr_1} {addr_2} {today}.xlsx" if not addr_3 or addr_3 == 'NaN' else f"{addr_1} {addr_2} {addr_3} {today}.xlsx"
            file_path = filedialog.asksaveasfilename(initialfile=filename, defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
            if file_path:
                listings_df.to_excel(file_path, index=False)
                messagebox.showinfo("성공", "스크래핑 완료 및 파일 저장 성공!")
            else:
                messagebox.showinfo("취소", "파일 저장이 취소되었습니다.")
        else:
            messagebox.showinfo("데이터 없음", "선택한 지역에 대한 데이터가 없습니다.")

    addr_1_menu.bind('<<ComboboxSelected>>', on_addr1_selected)
    addr_2_menu.bind('<<ComboboxSelected>>', on_addr2_selected)

    scrape_button = tk.Button(root, text="스크래핑 시작", command=scrape_and_save)
    scrape_button.pack(padx=10, pady=5)

    root.mainloop()

if __name__ == "__main__":
    file_path = 'D:\\Google 드라이브\\17. 코딩 공부\\Naver 매물\\B_CODE\\B_CODE_ADDR3.csv'  # Update with the actual path to the CSV file
    nested_dict = load_and_convert_csv(file_path)
    scrape_gui(nested_dict)
