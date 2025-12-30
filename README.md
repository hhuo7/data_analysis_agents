# AI Agents for Data Analysis and Visualization

A Streamlit-based Business Intelligence platform powered by AI agents for automated data analysis and visualization.

## Features

- **AI-Powered Analysis**: Automated data analysis using LangChain and OpenAI GPT models
- **Interactive Visualizations**: Generate charts and graphs from your data
- **Multi-Database Support**: Connect to SQLite databases with role-based access control
- **PDF Reports**: Export analysis results and visualizations to PDF
- **User Management**: Admin panel for managing database access permissions

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables:
   Create a `.env` file with:

```
OPENAI_API_KEY=your_openai_api_key_here
```

3. Run the application:

```bash
streamlit run app.py
```

## Functionality

1. **Login**: Select your user role from the sidebar
2. **Upload Database**: Admins can upload SQLite databases
3. **Select Database**: Choose from available databases
4. **Query Analysis**: Enter your analysis query in natural language
5. **View Results**: See AI-generated analysis summary, data tables, and visualizations
6. **Export PDF**: Download comprehensive reports

## Project Structure

- `app.py`: Main Streamlit application
- `agents/`: AI agent implementations
  - `analysis_agent.py`: Data analysis agent
  - `visualization_agent.py`: Chart generation agent
  - `workflow.py`: LangGraph workflow orchestration
  - `models.py`: Pydantic models and state definitions
- `manager.py`: Database and user management
- `tests/`:
   - `test_agents.py`: Unit tests
   - `test_integration.py`: Integration tests

## Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Usage

1. **Login**: Select your user role from the sidebar (admin, analyst, or manager)
2. **Database Management** (Admin only):
   - Go to Admin tab
   - Upload SQLite database files
   - Assign database access to users
3. **Data Analysis**:
   - Select a database from the dropdown
   - Enter your analysis query in natural language (e.g., "Show sales trends by month")
   - Choose a visual theme for the report
   - Click "Execute Workflow"
4. **View Results**:
   - Read the AI-generated executive summary
   - Explore the data table in the expandable section
   - View generated visualizations
5. **Export**: Download the complete analysis as a PDF report

### Example Queries

- "Analyze customer purchase patterns"
- "Compare revenue across different regions"
- "Show product performance metrics"
- "Identify sales trends over time"

