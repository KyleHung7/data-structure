import gspread
import pandas as pd
from google.oauth2.service_account import Credentials


# 設定 Google Service Account JSON 檔案
SERVICE_ACCOUNT_FILE = "service_account.json"

# 設定 API 權限範圍
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# 建立憑證物件
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# 使用 gspread 授權
gc = gspread.authorize(creds)

# **替換為你的 Google 試算表 URL**
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1OlKQx45xvfCgD3TwCSv7yA8cPFv45zhzM8Hr0sUN0_o/edit?usp=sharing"

# 開啟 Google 試算表
gsheets = gc.open_by_url(SPREADSHEET_URL)

# **選擇要讀取的工作表（第一個工作表）**
worksheet = gsheets.get_worksheet(0)

# **讀取 Google Sheets 內容**
data = worksheet.get_all_values()

# **轉換為 Pandas DataFrame**
df = pd.DataFrame(data[1:], columns=data[0])  # 第一行當作標題

# 顯示資料
print(df)

