import os
import asyncio
import pandas as pd
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer

load_dotenv()

async def process_reflection(user_journal, start_idx, total_records, model_client, termination_condition):
    """
    處理使用者的日記內容，提供正向建議並指出亮點。
    """
    prompt = (
        f"正在分析第 {start_idx} 至 {start_idx + len(user_journal) - 1} 筆日記內容（共 {total_records} 筆）。\n"
        "請基於每條使用者的日誌內容，提供具體的正向回饋：\n"
        "  1. 總結日誌中的積極面向；\n"
        "  2. 指出該內容中的亮點；\n"
        "  3. 提供有助於自信心提升的建議；\n"
        "  4. 使用 MultimodalWebSurfer 搜尋相關的激勵資訊，補充建議內容。\n"
    )
    
    start_page = "https://www.google.com"
    local_data_agent = AssistantAgent("data_agent", model_client)
    local_web_surfer = MultimodalWebSurfer("web_surfer", model_client, start_page)
    local_assistant = AssistantAgent("assistant", model_client)
    local_user_proxy = UserProxyAgent("user_proxy")
    local_team = RoundRobinGroupChat(
        [local_data_agent, local_web_surfer, local_assistant, local_user_proxy],
        termination_condition=termination_condition
    )
    
    messages = []
    async for event in local_team.run_stream(task=prompt):
        if isinstance(event, TextMessage):
            print(f"[{event.source}] => {event.content}\n")
            messages.append({
                "batch_start": start_idx,
                "batch_end": start_idx + len(user_journal) - 1,
                "source": event.source,
                "content": event.content,
                "type": event.type,
                "prompt_tokens": event.models_usage.prompt_tokens if event.models_usage else None,
                "completion_tokens": event.models_usage.completion_tokens if event.models_usage else None
            })
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
    
    csv_file_path = "predict_emotion_with_500_cases.csv"  # 用戶自己的日誌文件
    chunk_size = 500
    chunks = list(pd.read_csv(csv_file_path, chunksize=chunk_size))
    total_records = sum(chunk.shape[0] for chunk in chunks)
    
    tasks = list(map(
        lambda idx_chunk: process_reflection(
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
    output_file = "self_reflection_analysis.csv"
    df_log.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"已將分析結果輸出為 {output_file}")

if __name__ == '__main__':
    asyncio.run(main())

