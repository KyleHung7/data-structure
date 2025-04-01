import os
from datetime import datetime
import gradio as gr
import pandas as pd
from dotenv import load_dotenv
from fpdf import FPDF
import google.generativeai as genai
import re

# Load environment variables and set API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

def get_chinese_font_file() -> str:
    """
    Check if a Chinese font file exists in Windows Fonts directory.
    """
    fonts_path = r"C:\\Windows\\Fonts"
    candidates = ["kaiu.ttf"]  # Modify as needed
    for font in candidates:
        font_path = os.path.join(fonts_path, font)
        if os.path.exists(font_path):
            return os.path.abspath(font_path)
    return None

def create_table(pdf: FPDF, df: pd.DataFrame):
    """
    Render a pandas DataFrame as a table in the PDF.
    """
    available_width = pdf.w - 2 * pdf.l_margin
    num_columns = len(df.columns)
    col_width = available_width / num_columns
    cell_height = 10
    
    pdf.set_fill_color(200, 200, 200)
    pdf.set_font("ChineseFont", "", 12)
    
    # 表頭
    for col in df.columns:
        pdf.cell(col_width, cell_height, str(col), border=1, align="C", fill=True)
    pdf.ln(cell_height)

    fill = False
    for _, row in df.iterrows():
        if pdf.get_y() + cell_height > pdf.h - pdf.b_margin:
            pdf.add_page()
        
        if fill:
            pdf.set_fill_color(230, 240, 255)
        else:
            pdf.set_fill_color(255, 255, 255)

        for item in row:
            x = pdf.get_x()  # 記錄當前 X 座標
            y = pdf.get_y()  # 記錄當前 Y 座標
            pdf.multi_cell(col_width, cell_height, str(item), border=1, align="C", fill=True)
            pdf.set_xy(x + col_width, y)  # 調整 X 位置，確保不影響下一個單元格
        
        pdf.ln(cell_height)
        fill = not fill

def parse_markdown_table(markdown_text: str) -> pd.DataFrame:
    """
    Extract data from a Markdown table and return as a DataFrame.
    """
    lines = [line.strip() for line in markdown_text.strip().splitlines() if line.strip()]
    table_lines = [line for line in lines if line.startswith("|")]
    if not table_lines:
        return None
    headers = [h.strip() for h in table_lines[0].strip("|").split("|")]
    data = [[cell.strip() for cell in line.strip("|").split("|")] for line in table_lines[2:]]
    return pd.DataFrame(data, columns=headers)

def generate_pdf(text: str = None, df: pd.DataFrame = None) -> str:
    pdf = FPDF(format="A4")
    pdf.add_page()
    chinese_font_path = get_chinese_font_file()
    if not chinese_font_path:
        return "Error: No Chinese font found. Please install one."
    pdf.add_font("ChineseFont", "", chinese_font_path, uni=True)
    pdf.set_font("ChineseFont", "", 12)
    
    if df is not None:
        create_table(pdf, df)
    elif text:
        if "|" in text:
            table_part = "\n".join([line for line in text.splitlines() if line.strip().startswith("|")])
            parsed_df = parse_markdown_table(table_part)
            if parsed_df is not None:
                create_table(pdf, parsed_df)
            else:
                pdf.multi_cell(0, 10, text)
        else:
            pdf.multi_cell(0, 10, text)
    else:
        pdf.cell(0, 10, "No content available")
    
    pdf_filename = "TEST_output.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

def gradio_handler(csv_file, user_prompt):
    model = genai.GenerativeModel("gemini-2.5-pro-exp-03-25")  # 正確初始化 Gemini 模型
    
    if csv_file is not None:
        df = pd.read_csv(csv_file.name)
        total_rows = df.shape[0]
        block_size = 30
        cumulative_response = ""
        
        for i in range(0, total_rows, block_size):
            block = df.iloc[i:i+block_size]
            block_csv = block.to_csv(index=False)
            prompt = f"以下是CSV資料第 {i+1} 到 {min(i+block_size, total_rows)} 筆：\n{block_csv}\n\n{user_prompt}"
            
            response = model.generate_content(prompt)  # 修正 API 呼叫方式
            block_response = response.text.strip()
            cumulative_response += f"區塊 {i//block_size+1}:\n{block_response}\n\n"
        
        pdf_path = generate_pdf(text=cumulative_response)
        return cumulative_response, pdf_path
    else:
        response = model.generate_content(user_prompt)  # 修正 API 呼叫方式
        response_text = response.text.strip()
        pdf_path = generate_pdf(text=response_text)
        return response_text, pdf_path

default_prompt = """請根據以下的規則將每句對話進行分類...
"引導",
"評估(口語、跟讀的內容有關)",
"評估(非口語、寶寶自發性動作、跟讀的內容有關)",
"延伸討論",
"複述",
"開放式問題",
"填空",
"回想",
"人事時地物問句",
"連結生活經驗",
"備註"

並將所有類別進行統計後產出報表。"""

with gr.Blocks() as demo:
    gr.Markdown("# CSV 報表生成器")
    with gr.Row():
        csv_input = gr.File(label="上傳 CSV 檔案")
        user_input = gr.Textbox(label="請輸入分析指令", lines=10, value=default_prompt)
    output_text = gr.Textbox(label="回應內容", interactive=False)
    output_pdf = gr.File(label="下載 PDF 報表")
    submit_button = gr.Button("生成報表")
    submit_button.click(fn=gradio_handler, inputs=[csv_input, user_input], outputs=[output_text, output_pdf])

demo.launch()
