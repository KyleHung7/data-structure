# Multi-Agent Sentiment Analysis

This project is a Flask-based multi-agent real-time analysis system designed to analyze user-uploaded diary data and generate personalized emotional recommendations. Key features of the project include:

- Multiple AI agents working collaboratively to perform analysis and generate suggestions  
- Real-time display of each agent’s analysis process and output  
- Automatic extraction and display of the final recommendation for the user

## Feature Overview

- **Real-time Analysis Progress**: Uses Socket.IO to continuously update analysis progress, showing each agent’s actions and output.  
- **Multi-turn Interaction**: Supports multi-turn interactions among agents to ensure high-quality emotional recommendations.  
- **Instant Result Display**: Analysis results, including the extracted "final recommendation," are immediately returned to the frontend.  
- **Simplified Visualization**: A clean and minimal interface for progress tracking and recommendations enhances the user’s reading experience.

## How to Run the Project

1. Make sure you have Python 3.8 or above installed, along with the following dependencies:
    - Flask  
    - Python-dotenv  
    - Other necessary packages (see `requirements.txt`)

2. Set up environment variables:
    - Create a `.env` file  
    - Add the following content to the `.env` file:
      ```env
      GEMINI_API_KEY=your_openai_api_key
      ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Start the server:
    ```bash
    flask run
    ```
    By default, the server will run at `http://127.0.0.1:5000`.

5. Open your browser, upload your diary data through the web interface, and watch the real-time analysis progress.

## Code Overview

- **`app.py`**  
  The main Flask app entry point. Handles user uploads, triggers the analysis task, and returns the result to the frontend.

- **`multiagent.py`**  
  Implements the multi-agent analysis logic. Coordinates several AI agents to analyze the diary data and generate recommendations, and sends updates to the frontend via WebSocket.

- **`EMOwithSnow.py`**  
  Provides emotion analysis and trend chart generation for the diary data, saving the results as charts for frontend use.

- **`requirements.txt`**  
  Lists all Python packages and versions required for this project.

## Contribution and Feedback

Feel free to submit issues or pull requests to help us improve the system’s performance and user experience!


