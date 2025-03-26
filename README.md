# AutoGen Gemini Project

## Course Information
This project is part of the **Data Structure** course taught by **Professor Yun-Cheng Tsai**. The course focuses on hands-on practice to help students apply data structures to real-world problems.

### Course Objectives
1. **Practical Application**: Emphasize hands-on exercises to enable students to use data structures in solving real-world problems.
2. **Conceptual Understanding**: Enhance comprehension through theoretical explanations, real-world examples, and practical exercises.
3. **Intellectual Property Awareness**: Develop an understanding of the value and challenges of implementing theoretical concepts into practical programming frameworks, fostering respect for intellectual property rights.

## Overview
This project leverages the **Gemini API** (Large Language Model, LLM) with **AutoGen** to create AI agents that solve various problems efficiently. By utilizing AutoGen's multi-agent framework, we implement different use cases such as:
- Information retrieval
- Data analysis
- Interactive AI assistance

## Example Implementations

### 1. Multi-Agent File I/O Example (`dataAgent_playwright.py`)
This script demonstrates a multi-agent system using AutoGen, where agents collaborate to analyze CSV data and retrieve external information.

#### Features
- **Multi-Agent Collaboration**
  - **DataAgent & MultimodalWebSurfer**: Perform CSV data analysis and external information retrieval.
  - **UserProxyAgent**: Simulates user interactions.
- **Interactive Workflow**
  - Agents engage in an iterative loop until the conversation is terminated.

---

### 2. Batch Evaluation Process (`DRai.py`)
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

### Installation Steps:
```bash
python -m venv venv
.\venv\Scripts\activate

# Install AutoGen and dependencies
pip install -U autogen-agentchat autogen-ext[openai,web-surfer] python-dotenv
pip install autogen-agentchat python-dotenv playwright
playwright install

# Install AutoGen Studio
pip install -U autogenstudio
autogenstudio ui --port 8080 --appdir ./my-app
# Open in browser
http://localhost:8080

# If Playwright fails to install, use Selenium instead
pip install selenium webdriver-manager
pip install autogen selenium webdriver-manager
```
## Completed Tasks

### **AI_Agent_task1**
[Task File Path](https://github.com/KyleHung7/data-structure/tree/main/AI_Agent_task1)
- **Task**: Positive feedback for a journal with 500 cases.
- **Files**:
  - Input: `dataAgent_happy_journal.py`, `predict_emotion_with_500_cases.csv`
  - Output: `self_reflection_analysis.csv`



### **AI_Agent_task2**
[Task File Path](https://github.com/KyleHung7/data-structure/tree/main/AI_Agent_task2)
- **Task**: Detailed journal analysis with structured feedback:
  - Positive summary
  - Highlight strengths
  - Confidence-boosting suggestions
  - Motivational insights
- **Files**:
  - Input: `journal.py`, `journal.csv`
  - Output: `journal_output.csv`


  
### **AI_Agent_task3**
[Task File Path](https://github.com/KyleHung7/data-structure/tree/main/AI_Agent_task3)
- **Task**: Automate NTNU Moodle calendar task extraction and export:
  - Open NTNU Moodle and log in
  - Capture a screenshot after successful login
  - Navigate to the calendar page
  - Extract tasks and deadlines
  - Export data to a CSV file

- **Files**:
  - Input: `moodle.py`
  - Output: `moodle_login_success.png`, `calendar_events.csv`
    
## Upcoming Projects

### Flowchart for Future Developments:
![AI Agent](https://github.com/user-attachments/assets/55a6fda6-8e58-402e-8a32-1cdbd18dde6d)



