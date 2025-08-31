# Deep Research AI System

A comprehensive, agent-based research system that analyzes business ideas and provides detailed market research through interactive requirements gathering and automated research execution.

## What This Project Does

The Deep Research AI System is an intelligent research assistant that:

1. **Gathers Research Requirements**: Uses an interactive requirements gathering agent to understand your business idea through strategic questions
2. **Plans Research Strategy**: Creates comprehensive research plans tailored to your specific business concept
3. **Executes Deep Research**: Conducts automated web searches, market analysis, and competitive research
4. **Generates Professional Reports**: Produces detailed research reports with actionable insights, market analysis, and strategic recommendations

The system follows a sophisticated agent-based architecture where specialized AI agents work together to deliver comprehensive business research, from initial idea exploration to final market analysis.

## Quick Start

### Prerequisites
- Python 3.11 or higher
- UV package manager (recommended) or pip

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd deep_research
   ```

2. **Install dependencies using UV**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key
   TAVILY_API_KEY=your_tavily_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Run the system**:
   ```bash
   uv run python main.py
   ```

### Alternative Installation (using pip)
```bash
pip install -e .
python main.py
```

## Project Structure

```
deep_research/
├── main.py                          # Main entry point
├── pyproject.toml                   # Project configuration and dependencies
├── config/
│   ├── __init__.py
│   └── settings.py                  # Configuration settings and API keys
├── models/
│   ├── __init__.py
│   └── user_models.py              # Pydantic data models
├── ai_agents/
│   ├── __init__.py
│   ├── guardrail_agent.py          # Safety and validation agent
│   ├── orchestrator_agents.py      # Main orchestration logic
│   ├── requirements_agent.py       # Requirements gathering agent
│   └── research_agents.py          # Specialized research agents
├── services/
│   ├── __init__.py
│   ├── research_service.py         # Core research business logic
│   └── system_monitor.py           # System monitoring and logging
├── tools/
│   ├── __init__.py
│   ├── search_tools.py             # Web search and data collection tools
│   └── utility_tools.py            # Utility functions and helpers
├── utils/
│   ├── __init__.py
│   └── model_factory.py            # AI model initialization utilities
└── researches/                     # Output directory for research reports
```

## How It Works

### 1. Requirements Gathering
The system starts with an interactive requirements gathering agent that asks strategic questions about your business idea to understand:
- Target market and customer segments
- Business model and revenue streams
- Competitive advantages and unique value propositions
- Market entry strategy and goals

### 2. Research Planning
A planner agent creates a comprehensive research strategy based on your requirements, identifying key research areas such as:
- Market size and growth potential
- Competitive landscape analysis
- Customer behavior and preferences
- Financial viability and projections

### 3. Research Execution
The system executes the research plan using specialized agents:
- **Search Agent**: Conducts web searches, academic research, and data collection
- **Analysis Agent**: Analyzes market data, trends, and competitive information
- **Reports Agent**: Synthesizes findings into comprehensive reports

### 4. Report Generation
The final output includes:
- Executive summary with success probability assessment
- Detailed market analysis and competitive landscape
- Financial projections and viability assessment
- Risk factors and strategic recommendations
- Complete citations and data sources

## Configuration

Key configuration options in `config/settings.py`:
- `DEFAULT_USER_NAME`: Default user name for research sessions
- `DEFAULT_MAX_URLS`: Maximum URLs to analyze per search (default: 1)
- `MAX_QUESTIONS`: Maximum questions for requirements gathering (default: 3)
- `DEFAULT_SEARCH_DEPTH`: Search depth level (basic/advanced)

## Example Usage

```python
import asyncio
from models import UserPreference
from services import ResearchService
from ai_agents import create_requirements_gathering_agent, planner_agent

async def run_research():
    # Initialize the research service
    research_service = ResearchService()
    
    # Create user preferences
    user_preferences = UserPreference(
        name="Your Name",
        max_urls=3
    )
    
    # Gather research requirements
    requirements_agent = create_requirements_gathering_agent()
    research_requirements = await research_service.gather_requirements(requirements_agent)
    
    # Execute research plan
    await research_service.execute_research_plan(
        planner_agent, 
        research_requirements, 
        user_preferences
    )

# Run the research
asyncio.run(run_research())
```

## Dependencies

- **openai-agents**: AI agent framework for orchestration
- **tavily-python**: Web search and data collection
- **pydantic**: Data validation and settings management
- **python-dotenv**: Environment variable management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `uv run pytest`
5. Submit a pull request

## License

Developed and owned by Mehdi Raza Lakho
