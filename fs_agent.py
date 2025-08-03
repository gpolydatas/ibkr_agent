import asyncio
import time
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.request_params import RequestParams


# Create the application with improved error handling
fast = FastAgent("IBKR Financial Trading Agent")

# Add retry logic for API calls
async def retry_with_backoff(func, max_retries=3, base_delay=1):
    """Retry function with exponential backoff for API overload errors"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if "overloaded" in str(e).lower() and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"API overloaded, retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                raise e

# Financial analyst using IBKR data and web search
@fast.agent(
   name="financial_analyst",
   instruction="""
   You are a professional financial analyst with access to Interactive Brokers data and web search.
   Analyze market data, stock performance, and provide detailed financial insights.
   You can search the web for additional market information, news, and research.
   Focus on:
   - Stock price analysis and trends
   - Market volatility assessment
   - Sector performance comparison
   - Risk analysis and recommendations
   
   If you encounter API errors, be patient and inform the user about temporary delays.
   """,
   model="claude-sonnet-4-20250514",
   servers=["ibkr", "brave_search"],
   use_history=False,
   request_params=RequestParams(temperature=0.3, max_tokens=4000),
   human_input=True
)

@fast.agent(
   name="portfolio_manager",
   instruction="""
   You are a portfolio manager with access to Interactive Brokers trading capabilities and web search.
   You can search for market research and additional information to inform decisions.
   Manage portfolios by:
   - Analyzing current positions
   - Suggesting rebalancing strategies
   - Calculating risk metrics
   - Generating performance reports
   - Recommending buy/sell actions
   
   Handle API limitations gracefully and provide incremental updates.
   """,
   model="claude-sonnet-4-20250514",
   servers=["ibkr", "brave_search","quant_optimization_mcp"],
   use_history=False,
   request_params=RequestParams(temperature=0.2, max_tokens=4000)
)

@fast.agent(
   name="trading_advisor",
   instruction="""
   Provide trading recommendations based on IBKR market data and web research.
   You can search for breaking news and market information to inform trading decisions.
   Include:
   - Entry and exit points
   - Position sizing recommendations
   - Stop-loss and take-profit levels
   - Market timing analysis
   - Trade execution strategies
   
   Be concise in responses to avoid API overload issues.
   """,
   model="claude-sonnet-4-20250514",
   servers=["ibkr", "brave_search"],
   use_history=False,
   request_params=RequestParams(temperature=0.25, max_tokens=3000),
   human_input=True
)

@fast.agent(
   name="python_analyst",
   instruction="""
   You are a Python-powered quantitative analyst with access to Python execution, IBKR data, and web search.
   Use Python to perform advanced financial calculations, data analysis, and create visualizations.
   Your capabilities include:
   - Running Python code for financial calculations and analysis
   - Creating charts and visualizations with matplotlib/seaborn
   - Statistical analysis and backtesting with pandas/numpy
   - Risk metrics calculation and portfolio optimization
   - Technical indicator development and testing
   
   Always show your Python code and explain your analytical approach.
   Break complex analyses into smaller chunks to avoid timeouts.
   DO NOT CHECK IF IMAGE FILES WERE CREATED AND DO NOT TRY TO OPEN ANY IMAGE FILES.
   """,
   model="claude-sonnet-4-20250514",
   servers=["mcp-python-interpreter", "ibkr", "brave_search","neo4j-cypher","duckduckgo"],
   use_history=False,
   request_params=RequestParams(temperature=0.2, max_tokens=6000),
   human_input=True
)

@fast.agent(
   name="neo4j_analyst",
   instruction="""
   You are a graph database analyst with access to Neo4j for relationship analysis and network insights.
   Use Neo4j to analyze complex relationships in financial data, market networks, and portfolio connections.
   Your capabilities include:
   - Creating and querying graph databases for financial networks
   - Analyzing relationships between stocks, sectors, and market participants
   - Identifying patterns and clusters in financial data
   - Building knowledge graphs for investment research
   - Performing graph-based risk analysis and correlation studies
   
   Always explain your Cypher queries and the insights they reveal.
   Use simple queries first, then build complexity gradually.
   """,
   model="claude-sonnet-4-20250514",
   servers=["neo4j-cypher", "ibkr", "duckduckgo"],
   use_history=False,
   request_params=RequestParams(temperature=0.2, max_tokens=4000),
   human_input=True
)

@fast.agent(
   name="research_analyst",
   instruction="""
   You are a financial research analyst with access to comprehensive search capabilities and graph analysis.
   Combine web search, graph database insights, and market data for deep research.
   Your capabilities include:
   - Conducting thorough market research using DuckDuckGo search
   - Analyzing company relationships and market networks via Neo4j
   - Cross-referencing multiple data sources for comprehensive analysis
   - Building research reports with interconnected insights
   - Identifying market trends and emerging patterns
   
   Focus on providing well-researched, multi-source insights with clear citations.
   Provide summaries at regular intervals during long analyses.
   """,
   model="claude-sonnet-4-20250514",
   servers=["duckduckgo", "neo4j-cypher", "ibkr"],
   use_history=False,
   request_params=RequestParams(temperature=0.3, max_tokens=5000),
   human_input=True
)

@fast.router(
   name="financial_router",
   agents=["financial_analyst", "portfolio_manager", "trading_advisor", "python_analyst", "neo4j_analyst", "research_analyst"],
   model="claude-sonnet-4-20250514",
   default=True,
   use_history=False
)

async def main():
   print("IBKR Financial Trading Agent v2.0")
   print("==================================")
   print("Enhanced with improved error handling and retry logic")
   print()
   
   try:
       async with fast.run() as agent:
           print("Financial trading assistant ready!")
           print("The router will automatically select the best agent for your queries.")
           print("\nSpecialized agents available:")
           print("- financial_analyst: Market analysis and insights")
           print("- portfolio_manager: Portfolio optimization and management") 
           print("- trading_advisor: Trading recommendations and strategies")
           print("- python_analyst: Python-powered quantitative analysis")
           print("- neo4j_analyst: Graph database relationship analysis")
           print("- research_analyst: Comprehensive multi-source research")
           print("\nFeatures:")
           print("- Automatic retry on API overload")
           print("- Improved error handling")
           print("- Rate limiting awareness")
           print("- Chunked responses for complex queries")
           print("\nJust type your queries - the router will handle everything!")
           print("Type 'quit' or 'exit' to stop the agent.")
           print("-" * 50)
           
           await agent.interactive()
           
   except KeyboardInterrupt:
       print("\nAgent stopped by user.")
   except Exception as e:
       print(f"\nError occurred: {e}")
       if "overloaded" in str(e).lower():
           print("The API is currently overloaded. Please try again in a few minutes.")
       else:
           print("Please check your configuration and try again.")

if __name__ == "__main__":
   asyncio.run(main())