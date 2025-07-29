import asyncio
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.request_params import RequestParams


# Create the application
fast = FastAgent("IBKR Financial Trading Agent")

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
   """,
   model="claude-sonnet-4-20250514",
   servers=["ibkr", "brave_search"],
   use_history=True,
   request_params=RequestParams(temperature=0.3),
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
   """,
   model="claude-sonnet-4-20250514",
   servers=["ibkr", "brave_search"],
   use_history=True,
   request_params=RequestParams(temperature=0.2)
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
   """,
   model="claude-sonnet-4-20250514",
   servers=["ibkr", "brave_search"],
   use_history=True,
   request_params=RequestParams(temperature=0.25),
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
   """,
   model="claude-sonnet-4-20250514",
   servers=["mcp-python-interpreter", "ibkr", "brave_search"],
   use_history=True,
   request_params=RequestParams(temperature=0.2),
   human_input=True
)

@fast.router(
   name="financial_router",
   agents=["financial_analyst", "portfolio_manager", "trading_advisor", "python_analyst"],
   model="claude-sonnet-4-20250514",
   default=True,
   use_history=False
)

async def main():
   print("IBKR Financial Trading Agent")
   print("===========================")
   async with fast.run() as agent:
       print("Financial trading assistant ready!")
       print("The router will automatically select the best agent for your queries.")
       print("\nSpecialized agents available:")
       print("- financial_analyst: Market analysis and insights")
       print("- portfolio_manager: Portfolio optimization and management") 
       print("- trading_advisor: Trading recommendations and strategies")
       print("- python_analyst: Python-powered quantitative analysis")
       print("\nJust type your queries - the router will handle everything!")
       
       await agent.interactive()

if __name__ == "__main__":
   asyncio.run(main())