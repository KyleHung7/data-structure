from playwright.sync_api import sync_playwright
import os
import pandas as pd
from dotenv import load_dotenv

# 讀取 .env 檔案
load_dotenv()
MOODLE_USERNAME = os.getenv("MOODLE_USERNAME")
MOODLE_PASSWORD = os.getenv("MOODLE_PASSWORD")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 設為 False 方便 Debug
    page = browser.new_page()

    print("🔗 進入 Moodle 登入頁面...")
    page.goto("https://moodle3.ntnu.edu.tw/login/index.php")
    page.wait_for_timeout(5000)  # 等待 5 秒，確保頁面完全加載

    # 填入帳號與密碼
    page.fill("#username", MOODLE_USERNAME)
    page.fill("#password", MOODLE_PASSWORD)

    # 點擊登入按鈕
    page.click("#loginbtn")
    page.wait_for_timeout(5000)
    print("✅ 登入成功！")

    # 進入行事曆頁面
    page.goto("https://moodle3.ntnu.edu.tw/calendar/view.php?view=month")
    page.wait_for_selector("td[data-region='day']", timeout=60000)  # 最多等 60 秒
    print("📅 進入行事曆頁面...")

    # 抓取所有事件
    events = page.evaluate("""
        () => {
            let events = [];
            document.querySelectorAll("td[data-region='day']").forEach(day => {
                let date = day.querySelector("a[data-action='view-day-link']")?.innerText.trim();
                day.querySelectorAll("li[data-region='event-item']").forEach(event => {
                    let title = event.querySelector("a[data-action='view-event']")?.innerText.trim();
                    let link = event.querySelector("a[data-action='view-event']")?.href;
                    if (date && title && link) {
                        events.push({ "日期": date, "事件": title, "連結": link });
                    }
                });
            });
            return events;
        }
    """)

    if not events:
        print("⚠️ 沒有找到行事曆事件，請確認頁面是否正確加載")

    print(f"📌 共找到 {len(events)} 筆行事曆事件")

    # 存成 CSV
    df = pd.DataFrame(events)
    df.to_csv("calendar_events.csv", index=False, encoding="utf-8-sig")
    print("✅ 行事曆事件已匯出到 `calendar_events.csv`")

    # 關閉瀏覽器
    browser.close()
