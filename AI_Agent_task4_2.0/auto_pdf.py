import asyncio
from playwright.async_api import async_playwright
import os

async def run_playwright_automation(file_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        await page.goto("http://127.0.0.1:7860/")

        # 確認文件上傳元素是否存在
        file_input_locator = page.locator("input[type='file']")
        is_file_input_visible = await file_input_locator.is_visible()
        print(f"文件上傳元素是否可見: {is_file_input_visible}")

        # 強制顯示並移除禁用屬性
        if not is_file_input_visible:
            print("文件上傳元素未顯示，將強制顯示並移除禁用屬性。")
            await page.evaluate("""
                let fileInput = document.querySelector("input[type='file']");
                if (fileInput) {
                    fileInput.style.display = 'block';
                    fileInput.removeAttribute('disabled');
                }
            """)

        # 再次檢查是否可見
        is_file_input_visible = await file_input_locator.is_visible()
        print(f"文件上傳元素強制顯示後是否可見: {is_file_input_visible}")

        if is_file_input_visible:
            # 上傳檔案
            await file_input_locator.set_input_files(file_path)
            print("✅ 檔案已上傳")
        else:
            print("❌ 檔案上傳元素仍然無法顯示")

        # 點擊「生成分析報告」按鈕
        await page.click("#component-8")
        print("📝 已點擊生成分析報告，等待完成...")

        # 等待分析報告完成，出現「下載 PDF」按鈕（或其他元素）
        download_button = await page.wait_for_selector("button:has-text('下載 PDF')", timeout=60000)

        # 下載 PDF
        async with page.expect_download() as download_info:
            await download_button.click()
        download = await download_info.value

        save_path = os.path.join(os.getcwd(), "analysis_report.pdf")
        await download.save_as(save_path)
        print(f"✅ PDF 已下載到：{save_path}")

        await browser.close()

# 執行
if __name__ == "__main__":
    test_csv_path = r"D:\data_structure\autogen_project\AI_Agent_task4_2.0\journal_example.csv"
    asyncio.run(run_playwright_automation(test_csv_path))
