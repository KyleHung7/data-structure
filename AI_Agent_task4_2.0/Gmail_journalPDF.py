import os
import base64
import pickle
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import gradio as gr
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import pdfkit
from jinja2 import Template


# 🧩 設定 wkhtmltopdf 路徑
WKHTMLTOPDF_PATH = "D:/wkhtmltopdf/bin/wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

# 🌱 載入環境變數
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 📬 Gmail 發信的 SCOPES
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# 📩 Gmail 直接發送郵件功能
def send_email_with_pdf(receiver_email: str, subject: str, body: str, pdf_path: str):
    creds = None

    # token.pickle 儲存授權結果，避免每次都登入
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # 如果沒有有效憑證，讓使用者登入
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # 建立 Gmail API 服務
    service = build('gmail', 'v1', credentials=creds)

    # 建立郵件內容
    message = EmailMessage()
    message.set_content(body)
    message['To'] = receiver_email
    message['From'] = "me"
    message['Subject'] = subject

    # 加入 PDF 附件
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    message.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=os.path.basename(pdf_path))

    # 編碼 MIME 為 base64 並傳送
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {
        'raw': encoded_message
    }

    send_message = service.users().messages().send(userId="me", body=create_message).execute()
    print(f"✅ 郵件已寄出，ID：{send_message['id']}")

# 🧠 分析提示
default_prompt = """
你是一位語言分析專家，請根據以下評估項目分析日誌內容，並產生表格格式的回應：

| 日誌日期 | 日誌內容 | 積極面向總結 | 亮點指出 | 信心提升建議 | 激勵資訊補充 |
|---------|---------|------------|---------|-------------|-------------|
| {date} | {dialogue} |  |  |  |  |
"""

# 🧾 HTML 模板
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

# 📊 將 Markdown 表格轉為 DataFrame
def parse_markdown_table(markdown_text: str) -> pd.DataFrame:
    lines = [line.strip() for line in markdown_text.strip().splitlines() if line.strip()]
    table_lines = [line for line in lines if line.startswith("|")]
    if not table_lines or len(table_lines) < 3:
        return None
    headers = [h.strip() for h in table_lines[0].strip("|").split("|")]
    data = [[cell.strip() for cell in line.strip("|").split("|")] for line in table_lines[2:]]
    return pd.DataFrame(data, columns=headers)

# 📄 產生 HTML + PDF
def generate_html(df: pd.DataFrame) -> str:
    template = Template(HTML_TEMPLATE)
    return template.render(table=df)

def generate_pdf_from_html(html_content: str) -> str:
    pdf_filename = "journalPDF_output.pdf"
    pdfkit.from_string(html_content, pdf_filename, configuration=config)
    return pdf_filename

# 🧪 Gradio 分析流程
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
    else:
        response = model.generate_content(user_prompt)
        df_result = parse_markdown_table(response.text.strip())

    if df_result is not None:
        html_content = generate_html(df_result)
        pdf_path = generate_pdf_from_html(html_content)

        # 📬 自動寄送 PDF 郵件
        send_email_with_pdf(
            receiver_email="kyle973881@gmail.com",
            subject="AI 日誌分析報告",
            body="您好，這是由 AI 產生的日誌分析報告，請查收附件。\n\n祝好。",
            pdf_path=pdf_path
        )

        return html_content, pdf_path
    else:
        return "無法解析 AI 回應內容", None

# 🖥️ Gradio 介面
with gr.Blocks() as demo:
    gr.Markdown("### 📖 AI 日誌分析系統")
    with gr.Row():
        csv_input = gr.File(label="上傳 CSV 檔案")
        user_input = gr.Textbox(label="請輸入分析指令", lines=10, value=default_prompt)
    output_text = gr.HTML(label="HTML 預覽")
    output_pdf = gr.File(label="下載 PDF 報告")
    submit_button = gr.Button("生成分析報告並寄出")
    submit_button.click(fn=gradio_handler, inputs=[csv_input, user_input], outputs=[output_text, output_pdf])

demo.launch()
