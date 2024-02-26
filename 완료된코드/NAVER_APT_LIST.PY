from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openpyxl
from openpyxl import Workbook

def read_keywords_from_excel(file_path):
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    keywords = []
    for row in ws.iter_rows(min_row=2, min_col=4, max_col=4, values_only=True):
        if row[0] is not None:
            keywords.append(row[0])
    return keywords

def process_search_results(keyword):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "meta[property='og:url']")))
        current_url = driver.current_url
        if 'complexes' in current_url:
            complexNo = current_url.split('/complexes/')[1].split('?')[0]
            complexName = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "complexTitle"))).text
        else:
            raise Exception("Multiple results found")
    except Exception as e:
        try:
            apt_links = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[class*='item_link']")))
            for link in apt_links:
                if '아파트' in link.get_attribute('innerText'):
                    driver.execute_script("arguments[0].click();", link)
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "complexTitle")))
                    break
            complexNo = driver.current_url.split('/complexes/')[1].split('?')[0]
            complexName = driver.find_element(By.ID, "complexTitle").text
        except Exception as e:
            complexNo = '결과 없음'
            complexName = '결과 없음'

    new_ws.append([keyword, complexNo, complexName])

driver_path = 'C:\\Users\\beginplace2\\AppData\\Local\\SeleniumBasic\\chromedriver.exe'
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service)

new_wb = Workbook()
new_ws = new_wb.active

keywords = read_keywords_from_excel('D:\\Google 드라이브\\17. 코딩 공부\\TR_NAVER_INFO\\HW_TR_NAVER_INFO_TEST.xlsx')

for keyword in keywords:
    driver.get('https://new.land.naver.com/complexes/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'land_search')))
    search_item =  driver.find_element(By.CLASS_NAME, 'lnd_item')
    search_item.click()
    search_box = driver.find_element(By.ID, 'land_search')
    search_box.clear()
    search_box.send_keys(keyword)
    search_button = driver.find_element(By.CLASS_NAME, 'search_button')
    search_button.click()

    process_search_results(keyword)

# 엑셀 파일 저장
new_wb.save('결과.xlsx')

# 엑셀 파일 저장 시도
try:
    excel_path = 'D:\\Google 드라이브\\17. 코딩 공부\\TR_NAVER_INFO\\결과.xlsx'  # 혹은 절대 경로 사용, 예: 'C:/path/to/결과.xlsx'
    new_wb.save(excel_path)
    print(f"Excel file saved successfully at {excel_path}")
except Exception as e:
    print(f"Failed to save Excel file: {e}")

# 웹드라이버 종료
driver.quit()