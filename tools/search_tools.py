from agents import function_tool, RunContextWrapper
from tavily import AsyncTavilyClient
from config import TAVILY_API_KEY, DEFAULT_SEARCH_DEPTH
from models import UserPreference

# Initialize Tavily client
tavily_client = AsyncTavilyClient(api_key=TAVILY_API_KEY)

@function_tool
async def search_web(
    wrapper: RunContextWrapper[UserPreference] = None, 
    query: str = None, 
    search_depth: str = DEFAULT_SEARCH_DEPTH
) -> str:
    """
    Search the web for current information about a topic.
    
    Args:
        query: The search query
        search_depth: "basic" or "advanced"
        wrapper: The wrapper object containing user preferences
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
async def search_academic_papers(
    wrapper: RunContextWrapper[UserPreference] = None, 
    topic: str = None
) -> str:
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
async def search_market_reports(
    wrapper: RunContextWrapper[UserPreference] = None, 
    industry: str = None
) -> str:
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
async def search_competitors(
    wrapper: RunContextWrapper[UserPreference] = None, 
    product_name: str = None, 
    industry: str = None
) -> str:
    """
    Search for competitors and similar products in the market.
    """
    try:
        print(f"Searching for competitors about: {product_name}")
        response = await tavily_client.search(
            query=f"competitors similar products {product_name} {industry}",
            search_depth=DEFAULT_SEARCH_DEPTH,
            max_results=wrapper.context.max_urls
        )
        return f"Competitor analysis results for '{product_name}':\n{response}"
    except Exception as e:
        return f"Competitor search failed: {str(e)}"

@function_tool
async def search_financial_data(
    wrapper: RunContextWrapper[UserPreference] = None, 
    company_name: str = None, 
    industry: str = None
) -> str:
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
            search_depth=DEFAULT_SEARCH_DEPTH,
            include_domains=["*.com", "crunchbase.com", "pitchbook.com", "*.gov"],
            max_results=wrapper.context.max_urls
        )
        return f"Financial data results: {response}"
    except Exception as e:
        return f"Financial search failed: {str(e)}"
