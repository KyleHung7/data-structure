import os
import json
import pandas as pd
import gradio as gr
from dotenv import load_dotenv
import google.generativeai as genai

# 載入環境變數
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("❌ 環境變數 GEMINI_API_KEY 未設定！請確認 .env 檔案內容")

# 設定 Gemini API
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# 評估項目
ITEMS = ["積極面向總結", "亮點指出", "信心提升建議", "激勵資訊補充"]

def format_list_as_numbered_string(items):
    """將列表轉換為條列式字串"""
    return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items) if item.strip()])

def parse_response(response_text):
    """解析 Gemini API 回應 JSON，確保正確格式"""
    cleaned = response_text.strip()
    
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:] if lines[0].startswith("```") else lines
        lines = lines[:-1] if lines[-1].strip() == "```" else lines
        cleaned = "\n".join(lines).strip()
    
    try:
        result = json.loads(cleaned)
        return {item: format_list_as_numbered_string(result.get(item, [])) for item in ITEMS}
    except json.JSONDecodeError:
        return {item: "" for item in ITEMS}


def process_batch_dialogue(grouped_dialogues):
    """批量處理日誌，每天的內容獨立發送請求"""
    results = []
    
    for dialogue in grouped_dialogues:
        prompt = (
            "你是一位語言分析專家，請根據以下評估項目分析日誌內容：\n"
            + "\n".join(ITEMS) +
            "\n\n請產生 JSON 格式回應，每個項目需提供 3 個具體評估訊息。\n"
            "範例輸出：\n```json\n{\n  \"積極面向總結\": [\"內容1\", \"內容2\", \"內容3\"],\n  \"亮點指出\": [\"內容1\", \"內容2\", \"內容3\"],\n  ...\n}\n```"
            f"\n\n日誌內容：{dialogue}"
        )

        response = model.generate_content(prompt)

        # 解析回應
        parsed_result = parse_response(response.text)
        results.append(parsed_result)

    return results

def process_file(file_obj, chat_history):
    """處理上傳的 CSV 並進行分析"""
    if not file_obj:
        return chat_history, None

    try:
        # 讀取 CSV，避免因 BOM 而導致欄位名稱錯誤
        df = pd.read_csv(file_obj.name, encoding="utf-8-sig")

        # 標準化欄位名稱，去除多餘空白
        df.columns = df.columns.str.strip()

        # 確保 CSV 欄位名稱正確
        expected_columns = ["日誌日期", "日誌內容"]
        missing_columns = [col for col in expected_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"⚠️ CSV 檔案缺少必要欄位：{', '.join(missing_columns)}")

        # 轉換日期格式，確保分組不會錯誤
        df["日誌日期"] = pd.to_datetime(df["日誌日期"], errors="coerce").dt.strftime("%Y-%m-%d")

        # 確保沒有 NaN 日期
        df = df.dropna(subset=["日誌日期"])

        # 確保日誌內容是字串格式
        df["日誌內容"] = df["日誌內容"].astype(str)

        # 以日期為單位分組
        grouped = df.groupby("日誌日期", as_index=False).agg({"日誌內容": "\n".join})

        chat_history.append({"role": "system", "content": f"📄 正在分析 {len(grouped)} 天的日誌..."})

        batch_size = 5
        total = len(grouped)
        output_data = []

        for start_idx in range(0, total, batch_size):
            end_idx = min(start_idx + batch_size, total)
            dialogues = grouped.iloc[start_idx:end_idx]["日誌內容"].tolist()
            
            # 確保每個日誌內容分開處理
            batch_results = process_batch_dialogue(dialogues)

            for idx, row in enumerate(grouped.iloc[start_idx:end_idx].itertuples(index=False)):
                result = batch_results[idx]  # 確保索引對應正確

                if all(not result[item] for item in ITEMS):
                    continue

                output_data.append({
                    "日誌日期": row.日誌日期,  # 確保日期不會合併
                    "日誌內容": row.日誌內容,
                    **result
                })

                # 獨立加入 chat_history，而不是合併
                chat_history.append({
                    "role": "assistant",
                    "content": f"📅 **{row.日誌日期}**\n\n" + 
                               "\n\n".join([f"**{k}**:\n{v}" for k, v in result.items() if v])
                })

        if not output_data:
            chat_history.append({"role": "system", "content": "⚠️ 沒有有效的分析結果，請確認日誌內容格式。"})
            return chat_history, None

        output_df = pd.DataFrame(output_data)
        output_file = "journalUI_output.csv"
        output_df.to_csv(output_file, index=False, encoding="utf-8-sig")

        chat_history.append({"role": "system", "content": "✅ 分析完成！下載結果："})
        return chat_history, output_file

    except Exception as e:
        chat_history.append({"role": "system", "content": f"❌ 解析失敗：{str(e)}"})
        return chat_history, None

# 建立 Gradio 介面
with gr.Blocks() as demo:
    gr.Markdown("### 📖 AI 日誌分析系統")

    file_input = gr.File(label="上傳日誌 CSV")
    chat_display = gr.Chatbot(label="分析過程", type="messages")
    download_log = gr.File(label="下載分析結果")

    start_btn = gr.Button("開始分析")

    start_btn.click(
        fn=process_file,
        inputs=[file_input, chat_display],
        outputs=[chat_display, download_log]
    )

# 啟動 Web 介面
demo.queue().launch()
