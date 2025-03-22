import os
import asyncio
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import io

# 根據你的專案結構調整下列 import
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

def init_selenium():
    """初始化 Selenium WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

async def process_chunk(chunk, start_idx, total_records, model_client, termination_condition):
    chunk_data = chunk.to_dict(orient='records')

    # 檢查 chunk_data 是否為空
    if not chunk_data:
        print(f"⚠️ 跳過空的批次（第 {start_idx} - {start_idx + len(chunk) - 1} 筆）")
        return []

    prompt = (
        f"目前正在處理第 {start_idx} 至 {start_idx + len(chunk) - 1} 筆資料（共 {total_records} 筆）。\n"
        f"以下為該批次資料:\n{chunk_data}\n\n"
        "請根據以上資料進行分析，並提供完整的寶寶照護建議。"
        "其中請特別注意：\n"
        "  1. 分析寶寶的日常行為與照護需求；\n"
        "  2. 請 MultimodalWebSurfer 搜尋外部網站，找出最新的寶寶照護建議資訊（例如餵食、睡眠、尿布更換等），\n"
        "     並將搜尋結果整合進回覆中；\n"
        "  3. 最後請提供具體的建議和相關參考資訊。\n"
        "請各代理人協同合作，提供一份完整且具參考價值的建議。"
    )

    # 將資料轉成 dict 格式
    chunk_data = chunk.to_dict(orient='records')
    prompt = (
        f"目前正在處理第 {start_idx} 至 {start_idx + len(chunk) - 1} 筆資料（共 {total_records} 筆）。\n"
        f"以下為該批次資料:\n{chunk_data}\n\n"
        "請根據以上資料進行分析，並提供完整的寶寶照護建議。"
        "其中請特別注意：\n"
        "  1. 分析寶寶的日常行為與照護需求；\n"
        "  2. 使用 MultimodalWebSurfer 搜尋外部網站，找出最新的寶寶照護建議資訊（例如餵食、睡眠、尿布更換等），\n"
        "     並將搜尋結果整合進回覆中；\n"
        "  3. 最後請提供具體的建議和相關參考資訊。\n"
        "請各代理人協同合作，提供一份完整且具參考價值的建議。"
    )
    
    # 初始化 Selenium WebDriver
    driver = init_selenium()
    driver.get("https://www.google.com")
    
    local_data_agent = AssistantAgent("data_agent", model_client)
    local_assistant = AssistantAgent("assistant", model_client)
    local_user_proxy = UserProxyAgent("user_proxy")
    local_team = RoundRobinGroupChat(
        [local_data_agent, local_assistant, local_user_proxy],
        termination_condition=termination_condition
    )
    
    messages = []
    async for event in local_team.run_stream(task=prompt):
        if isinstance(event, TextMessage):
            print(f"[{event.source}] => {event.content}\n")
            messages.append({
                "batch_start": start_idx,
                "batch_end": start_idx + len(chunk) - 1,
                "source": event.source,
                "content": event.content,
                "type": event.type,
                "prompt_tokens": event.models_usage.prompt_tokens if event.models_usage else None,
                "completion_tokens": event.models_usage.completion_tokens if event.models_usage else None
            })
    
    driver.quit()
    return messages

async def main():
    gemini_api_key = os.environ.get("GEMINI_API_TOKEN")
    if not gemini_api_key:
        print("請檢查 .env 檔案中的 GEMINI_API_TOKEN。")
        return

    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash",
        api_key=gemini_api_key,
    )
    
    termination_condition = TextMentionTermination("exit")
    
    csv_file_path = "cuboai_baby_diary.csv"
    chunk_size = 1000
    chunks = list(pd.read_csv(csv_file_path, chunksize=chunk_size))
    total_records = sum(chunk.shape[0] for chunk in chunks)
    
    tasks = list(map(
        lambda idx_chunk: process_chunk(
            idx_chunk[1],
            idx_chunk[0] * chunk_size,
            total_records,
            model_client,
            termination_condition
        ),
        enumerate(chunks)
    ))
    
    results = await asyncio.gather(*tasks)
    all_messages = [msg for batch in results for msg in batch]
    
    df_log = pd.DataFrame(all_messages)
    output_file = "all_conversation_log.csv"
    df_log.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"已將所有對話紀錄輸出為 {output_file}")

if __name__ == '__main__':
    asyncio.run(main(), debug=True)
