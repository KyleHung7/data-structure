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
**Folder:** `example_code1`

This script demonstrates a multi-agent system using AutoGen, where agents collaborate to analyze CSV data and retrieve external information.

#### Features
- **Multi-Agent Collaboration**
  - **DataAgent & MultimodalWebSurfer**: Perform CSV data analysis and external information retrieval.
  - **UserProxyAgent**: Simulates user interactions.
- **Interactive Workflow**
  - Agents engage in an iterative loop until the conversation is terminated.

---

### 2. Batch Evaluation Process (`DRai.py`)
**Folder:** `example_code2_1.0`

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

---

### 3. Multi-Agent File I/O and Multi-Model UI Example (`multiDataAgentUI.py`)
**Folder:** `example_code2_2.0`

This script utilizes **Gradio + Gemini API + AutoGen AgentChat** to create a **baby care data analysis tool**. It reads baby care data from a CSV file, automatically summarizes it, and provides valuable recommendations.

#### Features
- **Interactive UI**: Built using Gradio for user-friendly interactions.
- **Multi-Agent System**: Integrates AutoGen AgentChat to perform data analysis and summarization.
- **LLM-Powered Insights**: Uses Gemini API to generate valuable baby care suggestions based on data trends.

### 4. PDF Report Generation and Analysis (getPDF.py)
**Folder:** `example_code4`

This script leverages **FPDF** to generate PDF reports from CSV or text data, offering an elegant display of tables with alternating background colors and automatic pagination.

#### Features
- **PDF Report Generation:** Uses FPDF to convert CSV or text data into a PDF report, featuring beautiful table displays with alternating background colors and auto-pagination.

- **Chinese Font Detection and Loading:** On Windows systems, the script searches for suitable Chinese fonts (e.g., kaiu.ttf) and loads them into the PDF report. If no compatible font is found, an error message is displayed.

- **Markdown Table Parsing:** Supports extracting data from Markdown-formatted tables and converting it into a pandas DataFrame, making it easy to present the data in table format in the PDF report.

- **Gradio User Interface:** Provides a Gradio-based web interface where users can upload CSV files and input custom analysis commands (default commands include scoring rules). The system processes the CSV data in blocks, calling the Gemini API for responses, and finally merges all responses to generate a downloadable PDF report for easy sharing.


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

# If you encounter a CP950 encoding error during testing, you may need to modify the playwright_controller.py file in the virtual environment. The issue might occur at line 68, where with open is used. Modify it as follows to ensure UTF-8 encoding
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "page_script.js"), "r", encoding="utf-8") as fh:
    self._page_script = fh.read()
```
## Completed Tasks

### **AI_Agent_task1**
[Task File Path](https://github.com/KyleHung7/data-structure/tree/main/AI_Agent_task1)
- **Task**: Positive feedback for what you type.
  - Positive summary
  - Highlight strengths
  - Confidence-boosting suggestions
  - Motivational insights
- **File**:
  - Input: `dataAgent_happy_journal.py`, `predict_emotion_with_500_cases.csv`
  - Output: `self_reflection_analysis.csv`
- **Picture**:
![task1](https://github.com/user-attachments/assets/b8d06ad7-2e06-4e9b-be4a-8924cbcd0af5)


### **AI_Agent_task2_1.0**
[Task File Path](https://github.com/KyleHung7/data-structure/tree/main/AI_Agent_task2_1.0)
- **Task**: Detailed journal analysis with structured feedback:
  - Positive summary
  - Highlight strengths
  - Confidence-boosting suggestions
  - Motivational insights
- **File**:
  - Input: `journal.py`, `journal.csv`
  - Output: `journal_output.csv`
- **Picture**:
![task2_1.0](https://github.com/user-attachments/assets/684163d5-0af5-418e-ac3b-995574890f3f)

### **AI_Agent_task2_2.0**
[Task File Path](https://github.com/KyleHung7/data-structure/tree/main/AI_Agent_task2_2.0)
- **Task**: Develop a user interface for journal analysis that provides structured feedback and generates CSV output.
  - Positive summary
  - Highlight strengths
  - Confidence-boosting suggestions
  - Motivational insights
- **File**:
  - Input: `journalUI.py`, `journal_example.csv`
  - Output: `journalUI_output.csv`
- **Picture**:
![task2_2 0](https://github.com/user-attachments/assets/88d1970d-a1f7-43fd-923a-77c4affce10c)

### **AI_Agent_task3**
[Task File Path](https://github.com/KyleHung7/data-structure/tree/main/AI_Agent_task3)
- **Task**: Automate NTNU Moodle calendar task extraction and upload to Google calendar:
  - Open NTNU Moodle and log in
  - Navigate to the calendar page
  - Capture a screenshot of NTNU Moodle calendar
  - Extract tasks and deadlines
  - Export data to a CSV file
  - Upload to Google calendar

- **File**:
  - Input: `moodle.py`
  - Output: `moodle_calendar_screenshot.png`, `calendar_events.csv`

- **Picture**:
  
![image](https://github.com/user-attachments/assets/281a211d-54ee-44a2-a6f4-30c8b9c24bc5) 
![image](https://github.com/user-attachments/assets/d515bd04-9e8a-41df-9b4d-7f6b69ebe54a)

- **Video**:

![task3](https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMDQzNzcxb3l0ZTE5eWhhb3d4dHJ3YWpqMHM0czdoaHFpcm50ZTZnbCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Kx20VhVnaSGZi4uS5v/giphy.gif)


### **AI_Agent_task4_1.0**
[Task File Path](https://github.com/KyleHung7/data-structure/tree/main/AI_Agent_task4_1.0)
- **Task**: Develop a user interface for journal analysis that provides structured feedback and generates PDF output.
  - Positive summary
  - Highlight strengths
  - Confidence-boosting suggestions
  - Motivational insights
- **File**:
  - Input: `journalPDF.py`, `journal_example.csv`
  - Output: `journalPDF_output.csv`
- **Picture**:
![image](https://github.com/user-attachments/assets/54f77bf0-e62d-4d72-abe0-ab82369c00e3)
![image](https://github.com/user-attachments/assets/f378db97-b7c6-4961-a8fc-871feb507721)


### **AI_Agent_task4_2.0**
[Task File Path](https://github.com/KyleHung7/data-structure/tree/main/AI_Agent_task4_2.0)
- **Task**: Develop a user interface for journal analysis that provides structured feedback and generates PDF output and send it to gmail.
  - Positive summary
  - Highlight strengths
  - Confidence-boosting suggestions
  - Motivational insights
- **File**:
  - Input: `gmail_journalPDF.py`, `journal_example.csv`
  - Output: `journalPDF_output.csv`
- **Picture**:
![image](https://github.com/user-attachments/assets/26c817ec-cdb3-4ef2-b6ec-93f104b0e7f0)
![image](https://github.com/user-attachments/assets/ff69639f-c147-4d8c-a030-acbc7de52028)

### **AI_Agent_task5**
- **Picture**:
[Task File Path](https://github.com/KyleHung7/data-structure/tree/main/AI_Agent_task5)
![image](https://github.com/user-attachments/assets/2efcf3da-67f3-4e6c-be34-d92da6bdedac)
![image](https://github.com/user-attachments/assets/69a6cf88-2017-42df-b7ff-27da1a181f17)

   
## Upcoming Projects

### Flowchart for Future Developments:
![AI Agent](https://github.com/user-attachments/assets/55a6fda6-8e58-402e-8a32-1cdbd18dde6d)



