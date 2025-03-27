from playwright.sync_api import sync_playwright
import os
import pandas as pd
import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import webbrowser

# 讀取 .env 檔案
load_dotenv()
MOODLE_USERNAME = os.getenv("MOODLE_USERNAME")
MOODLE_PASSWORD = os.getenv("MOODLE_PASSWORD")

# Google Calendar API 權限
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authenticate_google():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    
    return build("calendar", "v3", credentials=creds)

def fetch_moodle_calendar():
    current_month = datetime.datetime.now().month  # 取得當前月份
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("🔗 進入 Moodle 登入頁面...")
        page.goto("https://moodle3.ntnu.edu.tw/login/index.php")
        page.wait_for_timeout(3000)
        
        page.fill("#username", MOODLE_USERNAME)
        page.fill("#password", MOODLE_PASSWORD)
        page.click("#loginbtn")
        page.wait_for_timeout(3000)
        print("✅ 登入成功！")
        
        page.goto("https://moodle3.ntnu.edu.tw/calendar/view.php?view=month")
        page.wait_for_selector("td[data-region='day']", timeout=30000)
        print("📅 進入行事曆頁面...")
        page.wait_for_timeout(3000)
        
        screenshot_path = "moodle_calendar_screenshot.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 行事曆畫面已截圖: {screenshot_path}")

        events = page.evaluate(f"""
            () => {{
                let events = [];
                let month = "{current_month}";
                document.querySelectorAll("td[data-region='day']").forEach(day => {{
                    let date = day.querySelector("a[data-action='view-day-link']")?.innerText.trim();
                    if (!date || date.includes("月")) return;
                    
                    day.querySelectorAll("li[data-region='event-item']").forEach(event => {{
                        let title = event.querySelector("a[data-action='view-event']")?.innerText.trim();
                        let link = event.querySelector("a[data-action='view-event']")?.href;
                        if (date && title && link) {{
                            events.push({{"日期": date, "事件": title, "連結": link}});
                        }}
                    }});
                }});
                return events;
            }}
        """)
        
        if not events:
            print("⚠️ 沒有找到行事曆事件，請確認頁面是否正確加載")
        
        print(f"📌 共找到 {len(events)} 筆行事曆事件")
        df = pd.DataFrame(events)
        df.to_csv("calendar_events.csv", index=False, encoding="utf-8-sig")
        print("✅ 行事曆事件已匯出到 calendar_events.csv")
        
        browser.close()

def add_events_to_google_calendar():
    service = authenticate_google()
    csv_file = "calendar_events.csv"
    if not os.path.exists(csv_file):
        print(f"❌ 錯誤：找不到 {csv_file}，請先執行 Moodle 爬蟲程式！")
        return
    
    df = pd.read_csv(csv_file)
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    
    existing_events = service.events().list(calendarId="primary").execute().get("items", [])
    existing_titles = {event["summary"] for event in existing_events}
    
    for _, row in df.iterrows():
        try:
            day = int(row["日期"])
            formatted_date = f"{current_year}-{current_month:02d}-{day:02d}"
        except ValueError:
            print(f"⚠️ 無效的日期: {row['日期']}，跳過此事件！")
            continue
        
        if row["事件"] in existing_titles:
            print(f"🔄 事件已存在，跳過: {row['事件']}")
            continue
        
        event = {
            "summary": row["事件"],
            "start": {"date": formatted_date, "timeZone": "Asia/Taipei"},
            "end": {"date": formatted_date, "timeZone": "Asia/Taipei"},
            "description": f"詳細資訊請查看：{row['連結']}"
        }
        
        created_event = service.events().insert(calendarId="primary", body=event).execute()
        print(f"✅ 已新增事件: {created_event['summary']}")
    
    # 打開 Google Calendar
    webbrowser.open("https://calendar.google.com")


if __name__ == "__main__":
    fetch_moodle_calendar()
    add_events_to_google_calendar()