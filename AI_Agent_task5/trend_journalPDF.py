import os
import threading
import pandas as pd
import base64
import pickle
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.generativeai as genai
import pdfkit
from jinja2 import Template
from dotenv import load_dotenv
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

# 設置 Matplotlib 後端和字體
matplotlib.use('Agg')
matplotlib.rc('font', family='Microsoft JhengHei')

# 初始化 Flask 和 SocketIO
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Uploads'
socketio = SocketIO(app, async_mode='threading')

# 創建必要的資料夾
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 載入環境變數
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Gmail 發信的 SCOPES
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# 設置 wkhtmltopdf 路徑（根據你的安裝路徑調整）
WKHTMLTOPDF_PATH = r"D:\wkhtmltopdf\bin\wkhtmltopdf.exe"  # 替換為你的實際路徑
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

# 發送郵件的函數
def send_email_with_pdf(receiver_email: str, subject: str, body: str, pdf_path: str):
    creds = None
    try:
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
    except (EOFError, pickle.PickleError) as e:
        print(f"Error loading token.pickle: {e}. Re-authenticating...")
        creds = None
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')  # Delete corrupted file

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("credentials.json not found. Please download it from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    message = EmailMessage()
    message.set_content(body)
    message['To'] = receiver_email
    message['From'] = "me"
    message['Subject'] = subject

    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    message.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=os.path.basename(pdf_path))

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    send_message = service.users().messages().send(userId="me", body=create_message).execute()
    print(f"✅ 郵件已寄出，ID：{send_message['id']}")

# 繪製信心趨勢圖
def generate_mood_trend_plot(user_id, user_entries):
    output_dir = "static/moodtrend"
    os.makedirs(output_dir, exist_ok=True)

    # 轉換日期格式並排序
    user_entries["日誌日期"] = pd.to_datetime(user_entries["日誌日期"])
    user_entries = user_entries.sort_values("日誌日期")
    # 確保信心指數為數字
    user_entries["信心指數"] = pd.to_numeric(user_entries["信心指數"], errors="coerce")
    
    # 計算平均信心指數
    avg_confidence = user_entries["信心指數"].mean()

    plt.figure(figsize=(12, 6))
    sns.lineplot(x="日誌日期", y="信心指數", data=user_entries, marker="o", label="信心指數", color="green", errorbar=None)
    plt.axhline(y=avg_confidence, color='green', linestyle='--', label=f"信心平均 ({avg_confidence:.2f})")
    plt.xlabel("日期")
    plt.ylabel("信心指數")
    plt.title(f"用戶 {user_id} 的信心趨勢圖")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.ylim(0, 10)  # 信心指數範圍設為 0~10

    output_path = os.path.join(output_dir, f"mood_trend_{user_id}.png")
    plt.savefig(output_path)
    plt.close()

    return output_path

# 生成 HTML 報告
def generate_html(df_result):
    template_str = """
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <title>AI 日誌分析報告</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>AI 日誌分析報告</h1>
        <table>
            <tr>
                {% for col in columns %}
                <th>{{ col }}</th>
                {% endfor %}
            </tr>
            {% for row in data %}
            <tr>
                {% for value in row %}
                <td>{{ value }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    template = Template(template_str)
    html_content = template.render(
        columns=df_result.columns.tolist(),
        data=df_result.values.tolist()
    )
    return html_content

# 將 HTML 轉為 PDF
def generate_pdf_from_html(html_content):
    output_dir = "static/reports"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdfkit.from_string(html_content, pdf_path, configuration=config)
    return pdf_path

# 分析日誌內容並生成信心指數
def analyze_confidence(df, model):
    confidence_scores = []
    for content in df["日誌內容"]:
        prompt = f"分析以下日誌內容，評估其反映的信心程度（0-10 分，10 分表示最高信心），並僅返回分數：\n{content}"
        response = model.generate_content(prompt)
        try:
            score = float(response.text.strip())
            confidence_scores.append(score)
        except ValueError:
            confidence_scores.append(5.0)  # 若無法解析，給予中間值
    return confidence_scores

# 後端處理檔案上傳和分析
def background_task(file_path):
    try:
        df = pd.read_csv(file_path)
        user_id = os.path.splitext(os.path.basename(file_path))[0]

        # 驗證 CSV 欄位
        required_columns = ["日誌日期", "日誌內容"]
        if not all(col in df.columns for col in required_columns):
            socketio.emit('update', {'message': '❌ CSV 檔案缺少必要欄位（日誌日期、日誌內容）！'})
            return

        # 初始化 AI 模型
        model = genai.GenerativeModel("gemini-2.5-pro-exp-03-25")

        # 生成信心指數
        df["信心指數"] = analyze_confidence(df, model)

        # 產生信心趨勢圖
        plot_path = generate_mood_trend_plot(user_id, df)
        socketio.emit('plot_generated', {'plot_url': '/' + plot_path})

        # 分析日誌並生成詳細報告
        prompt = """
        你是一位語言分析專家，請根據以下日誌內容分析信心趨勢，並產生表格格式的回應：
        | 日誌日期 | 日誌內容 | 信心指數 | 積極面向總結 | 信心提升建議 |
        |---------|---------|----------|------------|-------------|
        """
        response = model.generate_content(prompt + df.to_string())
        
        # 解析 AI 回應為 DataFrame
        lines = [line.strip() for line in response.text.strip().splitlines() if line.strip()]
        table_lines = [line for line in lines if line.startswith("|")]
        if len(table_lines) >= 3:
            headers = [h.strip() for h in table_lines[0].strip("|").split("|")]
            data = [[cell.strip() for cell in line.strip("|").split("|")] for line in table_lines[2:]]
            df_result = pd.DataFrame(data, columns=headers)
        else:
            df_result = pd.DataFrame([["無法解析 AI 回應"]], columns=["結果"])

        html_content = generate_html(df_result)
        pdf_path = generate_pdf_from_html(html_content)

        # 發送郵件
        send_email_with_pdf(
            receiver_email="kyle973881@gmail.com",
            subject="AI 日誌分析報告",
            body="您好，這是由 AI 產生的日誌分析報告，專注於信心趨勢，請查收附件。",
            pdf_path=pdf_path
        )
        socketio.emit('update', {'message': '🟢 分析完成，報告已寄出！'})
    except Exception as e:
        socketio.emit('update', {'message': f"❌ 分析過程出現錯誤: {str(e)}"})

# 網頁路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        socketio.emit('update', {'message': '🟢 檔案上傳成功，開始分析中...'})
        thread = threading.Thread(target=background_task, args=(file_path,))
        thread.start()
        return 'File uploaded and processing started.', 200

if __name__ == '__main__':
    socketio.run(app, debug=True)