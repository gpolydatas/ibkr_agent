# IBKR Financial Trading Agent

A sophisticated multi-agent financial trading system that integrates Interactive Brokers (IBKR) API with Python analytics, web search capabilities, and intelligent routing. The system provides specialized agents for different aspects of financial analysis and trading.

## Features

- **Multi-Agent Architecture**: Specialized agents for different financial tasks
- **IBKR Integration**: Direct connection to Interactive Brokers for real-time data and trading
- **Python Analytics**: Execute Python code for quantitative analysis and visualizations
- **Web Search**: Access to market news and research via Brave Search
- **Intelligent Routing**: Automatic selection of the best agent for your queries

## Available Agents

1. **Financial Analyst** - Market analysis, stock performance, volatility assessment
2. **Portfolio Manager** - Portfolio optimization, rebalancing, performance reports
3. **Trading Advisor** - Trading recommendations, entry/exit points, risk management
4. **Python Analyst** - Quantitative analysis, backtesting, custom calculations
5. **Router** - Automatically selects the best agent for your query

## Prerequisites

### 1. Interactive Brokers Setup

**Download and Install IB Gateway or TWS:**
- Visit [Interactive Brokers](https://www.interactivebrokers.com/en/trading/tws.php)
- Download either:
  - **IB Gateway** (recommended for API access) - lightweight, API-focused
  - **Trader Workstation (TWS)** - full trading platform

**Configure API Access:**
1. Launch IB Gateway or TWS
2. Log in with your IBKR credentials
3. Go to **Configure** → **Settings** → **API** → **Settings**
4. Enable "Enable ActiveX and Socket Clients"
5. Add `127.0.0.1` to trusted IP addresses
6. Set socket port:
   - IB Gateway: `4001` (live) or `4002` (paper)
   - TWS: `7497` (paper) or `7496` (live)
7. **Important**: For testing, use paper trading account

**Paper Trading Account:**
- Create a paper trading account at [IBKR Paper Trading](https://www.interactivebrokers.com/en/trading/free-trial.php)
- This allows testing without real money

### 2. Python Environment Setup

**Install UV (Python Package Manager):**
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart terminal or source your shell profile
source ~/.bashrc  # or ~/.zshrc
```

**Create Project Directory:**
```bash
mkdir ibkr-trading-agent
cd ibkr-trading-agent
```

## Installation

### 1. Clone or Create Project Files

Create the following files in your project directory:

- `fs_agent.py` - Main agent application
- `ibkr_fast_mcp_server.py` - IBKR MCP server
- `brave_mcp_server.py` - Brave search MCP server
- `fastagent.config.yaml` - Configuration file
- `requirements.txt` - Python dependencies

### 2. Install Dependencies

**Create requirements.txt:**
```txt
fast-agent-mcp
fastmcp
ibapi
pydantic
pydantic-settings
aiohttp
requests
anthropic
```

**Install with UV:**
```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Install additional MCP tools
uvx install mcp-python-interpreter
```

### 3. Install Deno (for Python interpreter)

```bash
# Install Deno
curl -fsSL https://deno.land/x/install/install.sh | sh

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.deno/bin:$PATH"
```

### 4. Configuration

**Create `fastagent.config.yaml`:**
```yaml
# MCP Capabilities
capabilities:
  elicitation: {}

# Global API Key (replace with your Anthropic API key)
api_key: "your-anthropic-api-key-here"

mcp:
  servers:
    ibkr:
      command: "uv"
      args: ["run", "fastmcp", "run", "ibkr_fast_mcp_server.py"]
      elicitation:
        mode: "auto_cancel"
    
    brave_search:
      command: "uv"
      args: ["run", "fastmcp", "run", "brave_mcp_server.py"]
      elicitation:
        mode: "auto_cancel"
    
    mcp-python-interpreter:
      command: "uvx"
      args: [
        "mcp-python-interpreter",
        "--dir",
        "/your/working/directory",  # Replace with your path
        "--python-path",
        "/your/working/directory/.venv/bin/python"  # Replace with your path
      ]
      env:
        MCP_ALLOW_SYSTEM_ACCESS: "0"
      elicitation:
        mode: "auto_cancel"

# Models
models:
  default:
    provider: "anthropic"
    model: "claude-sonnet-4-20250514"

# Providers  
providers:
  anthropic:
    base_url: "https://api.anthropic.com"

# Global settings
settings:
  default_temperature: 0.7
  max_retries: 3
  mcp_timeout: 30
  debug: false
  human_input_timeout: 300
```

### 5. Environment Variables

**Get API Keys:**
1. **Anthropic API Key**: Get from [Anthropic Console](https://console.anthropic.com/)
2. **Brave Search API Key**: Get from [Brave Search API](https://api.search.brave.com/)

**Set up environment (optional - can be in config file):**
```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export BRAVE_API_KEY="your-brave-search-key"
```

## Usage

### 1. Start IBKR Connection

1. Launch **IB Gateway** or **TWS**
2. Log in with your account credentials
3. Ensure API settings are configured (see Prerequisites)
4. Keep the application running

### 2. Run the Trading Agent

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the agent
uv run fs_agent.py interactive
```

### 3. Using the Agent

The system starts with an intelligent router that automatically selects the best agent for your queries. Simply type your questions:

**Example Queries:**
```
Analyze AAPL stock performance and create Python visualizations

What's my current portfolio performance?

Should I buy Tesla stock right now?

Create a Python backtest for a momentum strategy

Get the latest news about the semiconductor sector

Calculate the Sharpe ratio for my current positions
```

**Manual Agent Selection:**
If you want to use specific agents:
```
@financial_analyst analyze MSFT trends
@python_analyst create a correlation matrix
@trading_advisor recommend entry points for QQQ
@portfolio_manager rebalance suggestions
```

## Troubleshooting

### IBKR Connection Issues

**Error: "Failed to connect to IBKR"**
1. Ensure IB Gateway/TWS is running and logged in
2. Check API settings are enabled
3. Verify ports: 4001 (Gateway) or 7497 (TWS Paper)
4. Confirm 127.0.0.1 is in trusted IPs

**Market Data Issues:**
1. Ensure you have market data subscriptions
2. Paper trading has limited real-time data
3. Some data may be delayed

### Python Environment

**Module Import Errors:**
```bash
# Reinstall dependencies
uv pip install --force-reinstall -r requirements.txt
```

**MCP Server Errors:**
```bash
# Check MCP tools installation
uvx list
uvx install mcp-python-interpreter
```

### Token Usage Issues

If you get "prompt too long" errors:
1. The router resets context automatically
2. Restart the agent to clear accumulated context
3. Use specific agents for complex tasks instead of router

## Project Structure

```
ibkr-trading-agent/
├── fs_agent.py                 # Main agent application
├── ibkr_fast_mcp_server.py    # IBKR MCP server
├── brave_mcp_server.py        # Brave search server
├── fastagent.config.yaml      # Configuration
├── requirements.txt           # Dependencies
├── .venv/                     # Virtual environment
└── README.md                  # This file
```

## Security Notes

- Use paper trading accounts for testing
- Never commit API keys to version control
- Keep IB Gateway/TWS updated
- Monitor your positions and orders
- The system can execute real trades if using live accounts

## API Rate Limits

- **Anthropic**: Varies by plan
- **IBKR**: ~50 requests per second
- **Brave Search**: Varies by plan

## Support

For issues:
1. Check IBKR connection and API settings
2. Verify all dependencies are installed
3. Check the logs for specific error messages
4. Ensure API keys are valid and have sufficient credits

## License

This project is for educational and personal use. Ensure compliance with:
- Interactive Brokers API terms
- Anthropic API terms  
- Brave Search API terms

**Disclaimer**: This software is for educational purposes. Trading involves risk. Always verify trades and use appropriate risk management.
