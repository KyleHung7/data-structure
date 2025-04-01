import os
from datetime import datetime
import gradio as gr
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import pdfkit
from jinja2 import Template

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
    pdf_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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
        
        # 解析 Markdown 轉換為 DataFrame
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
        
        # 解析 Markdown 轉換為 DataFrame
        df_result = parse_markdown_table(response_text)
        if df_result is not None:
            html_content = generate_html(df_result)
            pdf_path = generate_pdf_from_html(html_content)
            return html_content, pdf_path
        else:
            return "無法解析 AI 回應內容", None

# Gradio 介面
with gr.Blocks() as demo:
    gr.Markdown("# CSV 報表生成器")
    with gr.Row():
        csv_input = gr.File(label="上傳 CSV 檔案")
        user_input = gr.Textbox(label="請輸入分析指令", lines=10, value=default_prompt)
    output_text = gr.HTML(label="HTML 預覽")
    output_pdf = gr.File(label="下載 PDF 報表")
    submit_button = gr.Button("生成報表")
    submit_button.click(fn=gradio_handler, inputs=[csv_input, user_input], outputs=[output_text, output_pdf])

demo.launch()
