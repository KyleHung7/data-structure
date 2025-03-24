# AutoGen Gemini Project

## Overview
This project leverages the Gemini API (Large Language Model, LLM) with AutoGen to create AI agents that solve various problems efficiently. By using AutoGen's multi-agent framework, we implement different use cases such as:
- Information retrieval
- Data analysis
- Interactive AI assistance

## Example Implementations

### 1. Single Query Example (`main.py`)
- Loads the Gemini API key from `.env`.
- Uses `OpenAIChatCompletionClient` to connect to Gemini.
- Sends a query and prints the response in the terminal.

### 2. Multi-Agent Conversation Example (`multiAgent.py`)
- Builds a multi-agent team using AutoGen:
  - **AssistantAgent** & **MultimodalWebSurfer**: Handle responses and information retrieval.
  - **UserProxyAgent**: Simulates user interaction.
- Agents communicate in a loop until encountering the `"exit"` keyword.

### 3. Multi-Agent File I/O Example (`dataAgent.py`)
- Constructs a multi-agent team using AutoGen:
  - **DataAgent** & **MultimodalWebSurfer**: Perform CSV data analysis and external information retrieval.
  - **UserProxyAgent**: Simulates user interaction.
- Agents interact in a loop until the conversation is terminated.

### 4. Multi-Agent File I/O with UI Example (`multiDataAgentUI.py`)
- Integrates Gradio + Gemini API + AutoGen AgentChat.
- Develops a **Baby Care Data Analysis Tool** that:
  - Reads CSV-formatted baby care data.
  - Summarizes and analyzes data.
  - Provides valuable insights and recommendations.

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



