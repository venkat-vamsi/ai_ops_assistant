AI Ops Assistant: A multi-agent AI system that accepts natural language tasks, plans execution steps, calls real APIs, and returns structured results. Built with LLM-powered reasoning and third-party API integrations.

Architecture:

This project implements a multi-agent architecture with three specialized agents:

1. Planner Agent
- Converts natural language input into structured execution plans
- Uses LLM (Gemini) to generate JSON plans with steps and tool selections
- Validates plans before execution
- Handles task decomposition and dependency mapping

2. Executor Agent
- Executes planned steps sequentially
- Manages tool invocation (GitHub API, Weather API)
- Implements retry logic for failed API calls
- Resolves inter-step dependencies

3. Verifier Agent
- Validates execution results against original request
- Uses LLM to assess task completion
- Formats output for user presentation
- Provides completeness scores and suggestions

Flow:
User Input → Planner → Executor → Verifier → Structured Output
               ↓          ↓           ↓
             LLM      API Tools      LLM


Integrated API's:

1. GitHub API - Search repositories, get stars, descriptions, languages
2. OpenWeather API - Fetch current weather, temperature, conditions

Prerequisites:

- Python 3.8+
- API Keys:
  - Google Gemini API key
  - GitHub Personal Access Token (optional but recommended)
  - OpenWeather API key

Setup Instructions:

1. Clone the Repository

git clone <your-repo-url>
cd ai_ops_assistant

2. Install Dependencies

pip install -r requirements.txt

Also Install Rust

Open this site:
https://rustup.rs

Download and run rustup-init.exe

During installation:

Just press Enter for default options

Run this command if streamlit wasn't imported:

python -m pip install streamlit

Also if any issue with open AI
 run:
 python -m pip install --upgrade openai

If any issue with dot evn , run:

python -m pip install python-dotenv

3. Configure Environment Variables

Copy the example environment file:
cp .env.example 

Edit .env.example and add your API keys:

GEMINI_API_KEY=your_actual_gemini_api_key
GITHUB_TOKEN=your_github_personal_access_token
OPENWEATHER_API_KEY=your_openweather_api_key


How to Get API Keys:

Gemini API Key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key to your .env.example file

GitHub Personal Access Token:
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: public_repo (for public repositories)
4. Copy the token to your .env.example file

OpenWeather API Key:
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Go to API keys section
3. Copy your default API key or create a new one
4. Add to your .env.example file

4. Run the Application

streamlit run main.py


The application will open in your browser at `http://localhost:8501`


Project Structure

ai_ops_assistant/
├── agents/
│   ├── __init__.py
│   ├── planner.py      # Planner Agent - Task planning with LLM
│   ├── executor.py     # Executor Agent - Tool execution
│   └── verifier.py     # Verifier Agent - Result validation
├── tools/
│   ├── __init__.py
│   ├── github_tool.py  # GitHub API integration
│   └── weather_tool.py # OpenWeather API integration
├── llm/
│   ├── __init__.py
│   └── llm_client.py   # LLM client (Gemini)
├── main.py             # Streamlit UI entry point
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore patterns
└── README.md           # This file

Technical Details

LLM Usage
- Model: Google Gemini 2.5 Flash (via OpenAI-compatible API)
- Structured Outputs: JSON schema enforcement for planning and verification
- Temperature Settings: 
  - Planning: 0.3 (deterministic)
  - Verification: 0.2 (highly deterministic)

Error Handling
- Retry Logic: Up to 2 retries for failed API calls
- Graceful Degradation: Partial results returned when some steps fail
- Validation: Input validation at each agent level

example prompts:

Find top java projects and also weather in delhi
Find top python starred projects and also weather in banglore"# ai_ops_assistant" 
