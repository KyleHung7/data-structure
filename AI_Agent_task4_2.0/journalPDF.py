import os
from datetime import datetime
import gradio as gr
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import pdfkit
from jinja2 import Template
from playwright.sync_api import sync_playwright  # 引入 Playwright

# 設定 wkhtmltopdf 路徑
WKHTMLTOPDF_PATH = "D:/wkhtmltopdf/bin/wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

# 載入環境變數並設定 API 金鑰
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 預設的分析指令
default_prompt = """
你是一位語言分析專家，請根據以下評估項目分析日誌內容，並產生表格格式的回應：

| 日誌日期 | 日誌內容 | 積極面向總結 | 亮點指出 | 信心提升建議 | 激勵資訊補充 |
|---------|---------|------------|---------|-------------|-------------|
| {date} | {dialogue} |  |  |  |  |

請根據日誌內容填寫「積極面向總結」、「亮點指出」、「信心提升建議」和「激勵資訊補充」四個欄位各寫 3 個具體內容。
"""

# 定義 HTML 模板
HTML_TEMPLATE = """
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>日誌分析報告</h2>
    <table>
        <thead>
            <tr>
                {% for col in table.columns %}
                <th>{{ col }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in table.values %}
            <tr>
                {% for cell in row %}
                <td>{{ cell }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

# 解析 Markdown 表格
def parse_markdown_table(markdown_text: str) -> pd.DataFrame:
    lines = [line.strip() for line in markdown_text.strip().splitlines() if line.strip()]
    table_lines = [line for line in lines if line.startswith("|")]
    if not table_lines or len(table_lines) < 3:
        return None
    headers = [h.strip() for h in table_lines[0].strip("|").split("|")]
    data = [[cell.strip() for cell in line.strip("|").split("|")] for line in table_lines[2:]]
    return pd.DataFrame(data, columns=headers)

# 生成 HTML
def generate_html(df: pd.DataFrame) -> str:
    template = Template(HTML_TEMPLATE)
    return template.render(table=df)

# 轉換 HTML 到 PDF
def generate_pdf_from_html(html_content: str) -> str:
    pdf_filename = "journalPDF_output.pdf"  # 固定 PDF 名稱
    pdfkit.from_string(html_content, pdf_filename, configuration=config)
    return pdf_filename

# Gradio 處理邏輯
def gradio_handler(csv_file, user_prompt):
    model = genai.GenerativeModel("gemini-2.5-pro-exp-03-25")
    
    if csv_file is not None:
        df = pd.read_csv(csv_file.name)
        total_rows = df.shape[0]
        block_size = 30
        cumulative_response = ""
        
        for i in range(0, total_rows, block_size):
            block = df.iloc[i:i+block_size]
            block_csv = block.to_csv(index=False)
            prompt = f"以下是 CSV 資料第 {i+1} 到 {min(i+block_size, total_rows)} 筆：\n{block_csv}\n\n{user_prompt}"
            
            response = model.generate_content(prompt)
            block_response = response.text.strip()
            cumulative_response += f"區塊 {i//block_size+1}:\n{block_response}\n\n"
        
        df_result = parse_markdown_table(cumulative_response)
        if df_result is not None:
            html_content = generate_html(df_result)
            pdf_path = generate_pdf_from_html(html_content)
            return html_content, pdf_path
        else:
            return "無法解析 AI 回應內容", None
    else:
        response = model.generate_content(user_prompt)
        response_text = response.text.strip()
        df_result = parse_markdown_table(response_text)
        if df_result is not None:
            html_content = generate_html(df_result)
            pdf_path = generate_pdf_from_html(html_content)
            return html_content, pdf_path
        else:
            return "無法解析 AI 回應內容", None

# ➕ Playwright 一鍵自動擷取並分析
def full_auto_analysis(user_prompt):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # 可以設定為 headless=False 來觀察操作
        context = browser.new_context()
        page = context.new_page()

        # 模擬登入，並擷取日誌資料
        page.goto("https://your-care-platform.com")
        page.fill("input[name='username']", "your_username")
        page.fill("input[name='password']", "your_password")
        page.click("button[type='submit']")
        
        # 等待頁面加載完成
        page.wait_for_timeout(3000)

        # 擷取日誌資料
        log_data = """日誌日期,日誌內容
2025-04-10,今天我幫助了爺爺做復健運動，他笑得很開心。
2025-04-11,今天陪奶奶做手部活動，她說自己感覺有進步。
2025-04-12,今天幫助住民梳頭髮，氣氛很溫馨。
"""
        with open("output.csv", "w", encoding="utf-8") as f:
            f.write(log_data)

        browser.close()
    
    # 使用 Gradio 處理擷取到的資料
    with open("output.csv", "rb") as f:
        return gradio_handler(f, user_prompt)

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("### 📖 AI 日誌分析系統")
    with gr.Row():
        csv_input = gr.File(label="上傳 CSV 檔案")
        user_input = gr.Textbox(label="請輸入分析指令", lines=10, value=default_prompt)
    output_text = gr.HTML(label="HTML 預覽")
    output_pdf = gr.File(label="下載 PDF 報告")

    with gr.Row():
        submit_button = gr.Button("🧠 生成分析報告")
        auto_button = gr.Button("⚙️ 自動擷取＋分析")

    submit_button.click(fn=gradio_handler, inputs=[csv_input, user_input], outputs=[output_text, output_pdf])
    auto_button.click(fn=full_auto_analysis, inputs=[user_input], outputs=[output_text, output_pdf])

demo.launch()
