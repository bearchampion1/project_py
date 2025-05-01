from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
browser = webdriver.Chrome(options=options)
# 設定 Chrome 選項
options = Options()
options.add_argument('--headless')  # 無頭模式（不開視窗）
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 指定 ChromeDriver 路徑（根據實際位置修改）
service = Service('./chromedriver-win64/chromedriver.exe')

# 啟動瀏覽器
#browser = webdriver.Chrome(service=service, options=options)

try:
    # 前往證交所公司資訊頁面
    url = 'https://www.twse.com.tw/zh/listed/profile/company.html'
    browser.get(url)

    # 等待輸入框出現並可互動
    wait = WebDriverWait(browser, 20)
    input_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.form-control")))
    wait = WebDriverWait(browser, 30)  # 增加等待時間為 30 秒
    element = wait.until(EC.presence_of_element_located((By.ID, "label0")))

    print(element.is_displayed())
    # 輸入股票代碼，例如：2330（台積電）
    stock_code = '2330'
    input_element.clear()
    input_element.send_keys(stock_code)

    # 等待一會讓結果出現（可視需要調整）
    time.sleep(3)

    # 擷取畫面或其他資料
    print("✅ 成功輸入股票代碼：", stock_code)
    print("📌 頁面標題：", browser.title)

except Exception as e:
    print("❌ 錯誤：", str(e))

finally:
    browser.quit()
