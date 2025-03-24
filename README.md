# AutoGen Gemini Project

## Overview
This project leverages the Gemini API (Large Language Model, LLM) with AutoGen to create AI agents that solve various problems efficiently. By using AutoGen's multi-agent framework, we implement different use cases such as:
- Information retrieval
- Data analysis
- Interactive AI assistance

## Example Implementations

### 1. Multi-Agent File I/O Example (`dataAgent.py`)
- Constructs a multi-agent team using AutoGen:
  - **DataAgent** & **MultimodalWebSurfer**: Perform CSV data analysis and external information retrieval.
  - **UserProxyAgent**: Simulates user interaction.
- Agents interact in a loop until the conversation is terminated.



---

### 2.DRai.py

This script evaluates speech transcriptions in batches using the Google Gemini API.

#### Features
- **CSV Input Handling**
  - Selects the appropriate column for transcriptions (`text`, `utterance`, `content`, or `dialogue`).
- **Batch Processing**
  - Groups multiple transcriptions into a single batch request.
  - Formats results as JSON with a custom delimiter (`-----`).
- **API Integration**
  - Calls the Google Gemini API for evaluation.
  - Cleans and parses responses to ensure completeness.
- **Real-Time Output Writing**
  - Appends processed batches to `113_batch.csv` to prevent data loss.
- **Rate Limiting**
  - Implements a 1-second delay between batch requests to prevent exceeding API limits.


## Prerequisites
- **Python** 3.10+
- **pip**

### Install required Python packages:
```bash
pip install python-dotenv autogen-agentchat autogen-ext[openai] playwright
```
## Completed Tasks

### **AI_Agent_task1**
- **Task**: Positive feedback for a journal with 500 cases.
- **Files**:
  - Input: `dataAgent_happy_journal.py`, `predict_emotion_with_500_cases.csv`
  - Output: `self_reflection_analysis.csv`

### **AI_Agent_task2**
- **Task**: Detailed journal analysis with structured feedback:
  - Positive summary
  - Highlight strengths
  - Confidence-boosting suggestions
  - Motivational insights
- **Files**:
  - Input: `journal.py`, `journal.csv`
  - Output: `journal_output.csv`

## Upcoming Projects

### Flowchart for Future Developments:
![AI Agent](https://github.com/user-attachments/assets/55a6fda6-8e58-402e-8a32-1cdbd18dde6d)



