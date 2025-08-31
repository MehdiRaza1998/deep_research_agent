from agents import Agent, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, ModelSettings, handoff, input_guardrail, set_tracing_disabled, RunContextWrapper, SQLiteSession
import os
import asyncio
from agents.lifecycle import RunHooks
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
from tavily import TavilyClient, AsyncTavilyClient
from datetime import datetime
from pathlib import Path
from agents.extensions import handoff_filters



load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_client = AsyncTavilyClient(api_key=tavily_api_key)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL_LITE = "gemini-2.5-flash-lite"
MODEL = "gemini-2.5-flash"

def get_model():
    provider : AsyncOpenAI = AsyncOpenAI(
        api_key=GEMINI_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    model : OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
        model=MODEL,
        openai_client=provider,
    )
    return model

def get_model_lite():
    provider : AsyncOpenAI = AsyncOpenAI(
        api_key=GEMINI_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    model : OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
        model=MODEL_LITE,
        openai_client=provider,
    )
    return model


class UserPreference(BaseModel):
    name: str = Field(default="Mehdi", description="The name of the user")
    max_urls: int = Field(default=1, description="The maximum number of urls to search for")


@function_tool
async def search_web(wrapper: RunContextWrapper[UserPreference] = None, query: str = None, search_depth: str = "basic") -> str:
    """
    Search the web for current information about a topic.
    
    Args:
        query: The search query
        search_depth: "basic" or "advanced"
        wrapper: The wrapper object
    """
    try:
        print(f"Searching the web for: {query}")
        response = await tavily_client.search(
            query=query,
            search_depth=search_depth,
            include_domains=["*.edu", "*.gov", "*.org", "*.com"],
            max_results=wrapper.context.max_urls
        )
        return f"Search results for '{query}':\n{response}"
    except Exception as e:
        return f"Search failed: {str(e)}"

@function_tool
async def search_academic_papers(wrapper: RunContextWrapper[UserPreference] = None, topic: str = None) -> str:
    """
    Search for academic papers and research about a topic.
    """
    try:
        print(f"Searching for academic papers about: {topic}")
        response = await tavily_client.search(
            query=f"academic research papers {topic}",
            search_depth="advanced",
            include_domains=["*.edu", "arxiv.org", "researchgate.net", "scholar.google.com"],
            max_results=wrapper.context.max_urls
        )
        return f"Academic research results for '{topic}':\n{response}"
    except Exception as e:
        return f"Academic search failed: {str(e)}"

@function_tool
async def search_market_reports(wrapper: RunContextWrapper[UserPreference] = None, industry: str = None) -> str:
    """
    Search for market reports and industry analysis.
    """
    try:
        print(f"Searching for market reports about: {industry}")
        response = await tavily_client.search(
            query=f"market report industry analysis {industry} 2024 2025",
            search_depth="advanced",
            include_domains=["*.com", "*.org", "statista.com", "ibisworld.com", "mckinsey.com"],
            max_results=wrapper.context.max_urls
        )
        return f"Market report results for '{industry}':\n{response}"
    except Exception as e:
        return f"Market report search failed: {str(e)}"

@function_tool
async def search_competitors(wrapper: RunContextWrapper[UserPreference] = None, product_name: str = None, industry: str = None) -> str:
    """
    Search for competitors and similar products in the market.
    """
    try:
        print(f"Searching for competitors about: {product_name}")
        response = await tavily_client.search(
            query=f"competitors similar products {product_name} {industry}",
            search_depth="basic",
            max_results=wrapper.context.max_urls
        )
        return f"Competitor analysis results for '{product_name}':\n{response}"
    except Exception as e:
        return f"Competitor search failed: {str(e)}"

@function_tool
async def search_financial_data(wrapper: RunContextWrapper[UserPreference] = None, company_name: str = None, industry: str = None) -> str:
    """
    Search for financial data, funding information, and investment trends.
    """
    query = ""
    if company_name:
        query += f"{company_name} "
    if industry:
        query += f"{industry} "
    query += "funding investment financial data revenue"
    
    try:
        print(f"Searching for financial data about: {company_name} {industry}")
        response = await tavily_client.search(
            query=query,
            search_depth="basic",
            include_domains=["*.com", "crunchbase.com", "pitchbook.com", "*.gov"],
            max_results=wrapper.context.max_urls
        )
        return f"Financial data results: {response}"
    except Exception as e:
        return f"Financial search failed: {str(e)}"

class GuardrailOutput(BaseModel):
    output_info: str
    tripwire_triggered: bool    

guardrail_agent = Agent(
    name="guard_rail_agent",
    model=get_model_lite(),
    instructions="""You are a guardrail agent that validates business ideas. 

IMPORTANT: You must respond with ONLY valid JSON in the exact format:
{
    "output_info": "your validation message here",
    "tripwire_triggered": true/false
}

Do NOT wrap your response in markdown code blocks or any other formatting. Output ONLY the raw JSON.

Validation rules:
- If the input is a valid business idea, set tripwire_triggered to false
- If the input is NOT a valid business idea (greetings, questions, etc.), set tripwire_triggered to true
- Always provide a clear output_info message explaining your decision""",
    tools=[],   
    output_type=GuardrailOutput,
    model_settings=ModelSettings(
        temperature=0.1,  # Low temperature for consistent JSON output
    )
)

@input_guardrail
async def idea_guardrail(ctx: RunContextWrapper, agent : Agent, input : str) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input)   
    print(result.final_output)
    if result.final_output.tripwire_triggered:
        return GuardrailFunctionOutput(
            output_info="Failed",
            tripwire_triggered=True
        )
    else:
        return GuardrailFunctionOutput(
            output_info="Passed",
            tripwire_triggered=False
        )

class UserQuestioning(BaseModel):
    question: str = Field(default="", description="The question to ask the user")
    question_number: int = Field(default=0, description="The number of the question")
    requirements_confirmed: bool = Field(default=False, description="If the user agrees to the requirements, set this to true")
    max_questions_reached: bool = Field(default=False, description="If the user has reached the maximum number of questions, set this to true")
    requirements_summary: str = Field(default="", description="A summary of the requirements")

def setupAgentRequirementsGathering():
        
    requirements_gathering_agent : Agent = Agent(
        name="requirements_gathering_agent",
        model=get_model_lite(),
        instructions="""
        You are a Requirements Gathering Agent for business idea research. Your role is to: UNDERSTAND the user's business idea thoroughly, 
        ASK targeted questions to gather missing information, CLARIFY key aspects of the business concept, CONFIRM requirements before proceeding to research. 
        Ask up to 3 strategic questions to understand: Target market and customer segments, Core value proposition and differentiation, Business model and revenue streams, 
        Key challenges or concerns, Success criteria and goals. Guidelines: Ask one question at a time, Be specific and actionable, Focus on information needed for research, 
        Confirm understanding before ending, When you have enough information, set requirements_confirmed to true and summarize. Always be helpful and professional. 
        Your goal is to gather complete requirements for research.
        
        IMPORTANT: You must return a JSON object with the following structure:
        {
            "question": "your question here",
            "question_number": 1,
            "requirements_confirmed": false,
            "max_questions_reached": false
        }
        
        CRITICAL RULES:
        1. You can ask a MAXIMUM of 3 questions total
        2. Track question_number starting from 1
        3. When question_number reaches 3, set max_questions_reached to true and requirements_confirmed to true
        4. When requirements are confirmed do not ask any other question and end the conversation, set requirements_confirmed to true and provide a summary in the question field
        5. If you have enough information before 3 questions, set requirements_confirmed to true and provide a summary
        """,
        model_settings=ModelSettings(
            temperature=0.3,
        ),
        output_type=UserQuestioning,
        input_guardrails=[idea_guardrail],

        
    )
    return requirements_gathering_agent



async def call_agent_requirements_gathering(my_agent):
    print("\nCALLING AGENT ASYNC\n")
    session = SQLiteSession(session_id="requirements_gathering")
    idea_given = input("Idea: ").strip()
    try:
        result: Runner = await Runner.run(my_agent, idea_given, session=session)
        question_count = 0
        while True:
            print(f"\nQuestion {result.final_output.question_number}: {result.final_output.question}")
            question_count = result.final_output.question_number
            
            # Check if max questions reached or requirements confirmed
            if result.final_output.max_questions_reached or result.final_output.requirements_confirmed:
                if result.final_output.requirements_summary:
                    print(f"\nRequirements Summary: {result.final_output.requirements_summary}")
                print("\nRequirements gathering completed!")
                break
                
            user_response = input("Your response: ").strip()
            if not user_response:
                break
                
            # Pass the current question count to the agent
            context = f"Current question number: {question_count}. User response: {user_response}"
            result: Runner = await Runner.run(my_agent, context, session=session)
            
            # Additional safety check for max questions
            if question_count > 3:
                print("\nMaximum number of questions (3) reached. Ending requirements gathering.")
                break
        print("\nFinal result:", result.final_output) 
        research_requirements = result.final_output.requirements_summary
        return research_requirements
    except InputGuardrailTripwireTriggered as e:
        print("Guardrail triggerd")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

    

async def call_agent_planner(my_agent, research_requirements, user, system_monitor):
    print("\nCALLING AGENT ASYNC\n")
    session = SQLiteSession(session_id="planner")
    print("Research requirements: ", research_requirements)
    print("-Research planner started-")
    result: Runner = await Runner.run(my_agent, research_requirements, session=session, max_turns=20, context=user, hooks=system_monitor)
    print("\nFinal result:", result.final_output) 
    
    # Save the research output as a markdown file
    await save_research_to_markdown(result.final_output, research_requirements)
    
    return result.final_output

async def save_research_to_markdown(final_output, research_requirements):
    """Save the research output as a formatted markdown file."""
    
    # Create researches folder if it doesn't exist
    researches_dir = Path("researches")
    researches_dir.mkdir(exist_ok=True)
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"research_{timestamp}.md"
    filepath = researches_dir / filename
    
    # Create formatted markdown content
    markdown_content = f"""# Business Research Report

**Generated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}  
**Research Topic:** {research_requirements}

---

## Executive Summary

{final_output}

---

*This report was generated by the Deep Research AI system using comprehensive web research, market analysis, and competitive intelligence.*

"""
    
    # Write to file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"\n✅ Research saved to: {filepath}")
    except Exception as e:
        print(f"\n❌ Error saving research file: {e}")


class ResearchPlan(BaseModel):
    research_plan: str = Field(default="", description="The research plan")


search_agent : Agent = Agent(
    name="search_agent",
    model=get_model(),
    instructions="""
    You are a Search Agent specializing in comprehensive web research. Your role is to:
        
        1. CONDUCT thorough web searches using multiple search tools
        2. GATHER information from various sources (general web, academic, market reports)
        3. SEARCH for competitors and market intelligence
        4. FIND financial data and investment information
        5. PROVIDE well-sourced research findings
        
        You have access to specialized search tools:
        - General web search for broad information
        - Academic paper search for scholarly research
        - Market reports search for industry analysis
        - Competitor search for competitive intelligence
        - Financial data search for investment information
        
        Always:
        - Use multiple sources to validate information
        - Prioritize recent and authoritative sources
        - Extract specific figures and data points
        - Provide citations and sources
        - Focus on actionable insights
        
        Your research should be thorough, accurate, and provide the foundation for analysis.
        """,
    tools=[
        search_web,
        search_academic_papers,
        search_market_reports,
        search_competitors,
        search_financial_data,
    ],
    # model_settings=ModelSettings(
    #     tool_choice="auto",
    #     parallel_tool_calls=True  # Use multiple tools simultaneously
    # )
)

analysis_agent : Agent = Agent(
    name="analysis_agent",
    model=get_model(),
    instructions="""
    You are an Analysis Agent for business research. Your role is to: ANALYZE the data and calculate metrics.
    """,
)


reports_agent : Agent = Agent(
    name="reports_agent",
    model=get_model(),
    instructions="""
    You are a Reports Agent for business research. Your role is to: CREATE reports.
    """,
)

@function_tool
def get_today_date():
    """
    Get the current date.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


orchestrator_agent : Agent = Agent(
    name="orchestrator_agent",
    model=get_model(),
    instructions="""
    You are a Lead Orchestrator Agent for business research. Your role is to:
    
    1. RECEIVE research plans from the Planner Agent
    2. COORDINATE research execution using specialized agent tools
    3. ORCHESTRATE the complete research workflow
    4. DELIVER comprehensive research reports
    
    You have access to specialized agent tools:
    
    - SEARCH_AGENT: Conducts web searches, academic research, market reports, competitor analysis, and financial data gathering
    - ANALYSIS_AGENT: Analyzes market data, conducts competitive analysis, calculates financial projections, extracts citations, and calculates success probabilities
    - REPORTS_AGENT: Creates comprehensive research reports, executive summaries, and professional documentation
    
    Research Workflow:
    1. Use the search_agent to gather comprehensive information about the business idea
    2. Use the analysis_agent to analyze the gathered data and calculate metrics
    3. Use the reports_agent to create the final research report
    
    CRITICAL: After using each tool, you MUST synthesize the results and provide a comprehensive final output.
    
    Your final output should include:
    - Executive Summary of the research findings
    - Market analysis and competitive landscape
    - Financial projections and viability assessment
    - Success probability and risk assessment
    - Strategic recommendations and next steps
    - Complete citations and references
    
    IMPORTANT: Do not end your response until you have provided a complete, comprehensive research report that synthesizes all the information gathered from your tools.
    
    Always:
    - Coordinate between agents effectively
    - Ensure comprehensive research coverage
    - Maintain research quality and accuracy
    - Provide actionable insights and recommendations
    - Deliver professional, well-structured reports
    - Synthesize all tool results into a final comprehensive report
    
    Your goal is to deliver comprehensive, actionable research that helps evaluate business ideas.
    """,
    tools=[
        search_agent.as_tool(tool_name="search_agent", tool_description="A tool for searching the web"),
        analysis_agent.as_tool(tool_name="analysis_agent", tool_description="A tool for analyzing the data"),
        reports_agent.as_tool(tool_name="reports_agent", tool_description="A tool for creating reports"),
        get_today_date,
    ],
)


planner_agent : Agent = Agent(
    name="strategic_planner_agent",
    model=get_model(),
    instructions="""
    You are a Strategic Research Planner Agent. Your role is to:
    
    1. UNDERSTAND the business idea and requirements
    2. CREATE a comprehensive research plan
    3. HAND OFF to the Lead Orchestrator Agent for execution

    When given a business idea and requirements, you should:
    - Break down the idea into research components
    - Identify key research areas (market, competition, financial, etc.)
    - Create a structured research plan
    - Hand off to the lead_orchestrator agent for execution
    
    Your research plan should include:
    - Market analysis requirements
    - Competitive landscape research
    - Financial projections and viability
    - Success probability assessment
    - Timeline and resource estimates
    
    Be thorough but practical - focus on the most critical research areas.
    Once you have a plan, return the research plan and hand off to the lead_orchestrator agent for execution.
    """,
    handoffs=[handoff(agent=orchestrator_agent, input_filter=handoff_filters.remove_all_tools)],
    model_settings=ModelSettings(
        temperature=0.3,
    ),
    # output_type=ResearchPlan,
)

class SystemMonitor(RunHooks):
    def __init__(self):
        self.active_agents = []
        self.tool_usage = {}
        self.handoffs = 0
    
    async def on_agent_start(self, context, agent):
        self.active_agents.append(agent.name)
        print(f"🌅 SYSTEM: {agent.name} is now working")
        print(f"   Active agents so far: {self.active_agents}")
    
    async def on_llm_start(self, context, agent, system_prompt, input_items):
        print(f"📞 SYSTEM: {agent.name} is thinking...")
    
    async def on_llm_end(self, context, agent, response):
        print(f"🧠✨ SYSTEM: {agent.name} finished thinking")
    
    async def on_tool_start(self, context, agent, tool):
        tool_name = tool.name
        if tool_name not in self.tool_usage:
            self.tool_usage[tool_name] = 0
        self.tool_usage[tool_name] += 1
        print(f"🔨 SYSTEM: {tool_name} used {self.tool_usage[tool_name]} times")
    
    async def on_tool_end(self, context, agent, tool, result):
        print(f"✅🔨 SYSTEM: {agent.name} finished using {tool.name}")
    
    async def on_handoff(self, context, from_agent, to_agent):
        self.handoffs += 1
        print(f"🏃‍♂️➡️🏃‍♀️ HANDOFF #{self.handoffs}: {from_agent.name} → {to_agent.name}")
    
    async def on_agent_end(self, context, agent, output):
        print(f"✅ SYSTEM: {agent.name} completed their work")
        print(f"📊 STATS: {len(self.active_agents)} agents used, {self.handoffs} handoffs")

# requirments gathering
agent_requirements_gathering = setupAgentRequirementsGathering()
research_requirements = asyncio.run(call_agent_requirements_gathering(agent_requirements_gathering))

# research_requirements ="""The business idea is an agentic AI approach for NLP to data fetching. 
#  It will automate the creation of such systems based on user-provided project details. The initial focus for data sources is SQL databases. 
#  The primary value proposition is the automated system design and creation. The revenue model is subscription-based."""



user = UserPreference(name="Mehdi", max_urls=1)


system_monitor = SystemMonitor()

# planner and later hand off to orchestrator
if research_requirements:
    asyncio.run(call_agent_planner(planner_agent, research_requirements, user, system_monitor))
else:
    print("No research requirements found")
