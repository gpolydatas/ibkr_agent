# IBKR Financial Trading Agent v2.0
A sophisticated multi-agent financial trading system that integrates Interactive Brokers (IBKR) API with Python analytics, web search capabilities, graph database analysis, and intelligent routing. The system provides specialized agents for different aspects of financial analysis and trading.

## Features
- **Multi-Agent Architecture**: Specialized agents for different financial tasks
- **IBKR Integration**: Direct connection to Interactive Brokers for real-time data and trading
- **Python Analytics**: Execute Python code for quantitative analysis and visualizations
- **Web Search**: Access to market news and research via Brave Search and DuckDuckGo
- **Graph Database Analysis**: Neo4j integration for relationship and network analysis
- **Quantitative Optimization**: Advanced portfolio optimization capabilities
- **Intelligent Routing**: Automatic selection of the best agent for your queries
- **Enhanced Error Handling**: Retry logic with exponential backoff for API overload
- **Elicitation Support**: Interactive prompting and confirmation capabilities

## Available Agents

### Core Trading Agents
- **Financial Analyst** - Market analysis, stock performance, volatility assessment
- **Portfolio Manager** - Portfolio optimization, rebalancing, performance reports
- **Trading Advisor** - Trading recommendations, entry/exit points, risk management

### Advanced Analytics Agents
- **Python Analyst** - Quantitative analysis, backtesting, custom calculations with full Python execution
- **Neo4j Analyst** - Graph database analysis for relationship insights and network patterns
- **Research Analyst** - Comprehensive multi-source research with cross-referencing capabilities

### Routing
- **Router** - Automatically selects the best agent for your query with improved context management

## Prerequisites

### 1. Interactive Brokers Setup
**Download and Install IB Gateway or TWS:**
- Visit [Interactive Brokers](https://www.interactivebrokers.com)
- Download either:
  - **IB Gateway** (recommended for API access) - lightweight, API-focused
  - **Trader Workstation (TWS)** - full trading platform

**Configure API Access:**
1. Launch IB Gateway or TWS
2. Log in with your IBKR credentials
3. Go to Configure → Settings → API → Settings
4. Enable "Enable ActiveX and Socket Clients"
5. Add `127.0.0.1` to trusted IP addresses
6. Set socket port:
   - IB Gateway: 4001 (live) or 4002 (paper)
   - TWS: 7497 (paper) or 7496 (live)

**Important**: For testing, use paper trading account

**Paper Trading Account:**
- Create a paper trading account at [IBKR Paper Trading](https://www.interactivebrokers.com/en/trading/free-trial.php)
- This allows testing without real money

### 2. Docker Setup (New Requirement)
Install Docker for the Neo4j and DuckDuckGo services:

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in to apply group changes
```

**On macOS:**
```bash
# Install Docker Desktop from https://docker.com/products/docker-desktop
```

**On Windows:**
- Install Docker Desktop from https://docker.com/products/docker-desktop

### 3. Neo4j Database Setup
**Option 1: Docker Neo4j (Recommended)**
```bash
# Pull and run Neo4j container
docker run --name neo4j-trading \
    -p 7474:7474 -p 7687:7687 \
    -d \
    -e NEO4J_AUTH=neo4j/password \
    -e NEO4J_PLUGINS='["apoc"]' \
    neo4j:latest

# Verify Neo4j is running
docker ps
```

**Option 2: Local Neo4j Installation**
1. Download from [Neo4j Download Center](https://neo4j.com/download/)
2. Install and start the database
3. Set username: `neo4j`, password: `password`
4. Ensure it's running on default ports (7474 HTTP, 7687 Bolt)

### 4. Python Environment Setup
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

### 5. Install Deno (for Python interpreter)
```bash
# Install Deno
curl -fsSL https://deno.land/x/install/install.sh | sh

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.deno/bin:$PATH"
```

## Installation

### 1. Clone or Create Project Files
Create the following files in your project directory:
- `fs_agent.py` - Main agent application
- `ibkr_fast_mcp_server.py` - IBKR MCP server
- `brave_mcp_server.py` - Brave search MCP server
- `quant_optimization_mcp.py` - Quantitative optimization server (NEW)
- `fastagent.config.yaml` - Configuration file
- `requirements.txt` - Python dependencies

### 2. Install Dependencies
**Create requirements.txt:**
```
fast-agent-mcp
fastmcp
ibapi
pydantic
pydantic-settings
aiohttp
requests
anthropic
numpy
pandas
scipy
matplotlib
seaborn
scikit-learn
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

### 3. Pull Required Docker Images
```bash
# Pull Neo4j Cypher MCP server
docker pull mcp/neo4j-cypher

# Pull DuckDuckGo MCP server  
docker pull mcp/duckduckgo
```

### 4. Configuration
**Create fastagent.config.yaml:**

```yaml
# MCP Capabilities - ADD ELICITATION SUPPORT
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
    
    # NEW: Quantitative Optimization Server
    quant_optimization_mcp:
      command: "uv"
      args: ["run", "fastmcp", "run", "quant_optimization_mcp.py"]
      elicitation:
        mode: "auto_cancel"
    
    mcp-python-interpreter:
      command: "uvx"
      args: [
        "mcp-python-interpreter",
        "--dir",
        "/your/working/directory",  # Replace with your actual path
        "--python-path",
        "/your/working/directory/.venv/bin/python"  # Replace with your actual path
      ]
      env:
        MCP_ALLOW_SYSTEM_ACCESS: "0"
      elicitation:
        mode: "auto_cancel"
    
    # NEW: Neo4j Graph Database Integration
    neo4j-cypher:
      command: "docker"
      args: [
        "run",
        "-i",
        "--rm",
        "-e", "NEO4J_URL=bolt://host.docker.internal:7687",
        "-e", "NEO4J_USERNAME=neo4j", 
        "-e", "NEO4J_PASSWORD=password",
        "mcp/neo4j-cypher"
      ]
      elicitation:
        mode: "auto_cancel"
    
    # NEW: DuckDuckGo Search Integration
    duckduckgo:
      command: "docker"
      args: [
        "run",
        "-i",
        "--rm",
        "mcp/duckduckgo"
      ]
      elicitation:
        mode: "auto_cancel"

# Models with aliases for different use cases
models:
  default:
    provider: "anthropic"
    model: "claude-sonnet-4-20250514"
  
  # NEW: Model aliases for different performance needs
  aliases:
    fast: "claude-haiku-3-20240307"
    balanced: "claude-sonnet-4-20250514" 
    powerful: "claude-opus-3-20240229"

# Providers  
providers:
  anthropic:
    base_url: "https://api.anthropic.com"

# Global settings with enhanced error handling
settings:
  default_temperature: 0.7
  max_retries: 3
  mcp_timeout: 30
  debug: false
  human_input_timeout: 300
```

### 5. Environment Variables
**Get API Keys:**
- **Anthropic API Key**: Get from [Anthropic Console](https://console.anthropic.com)
- **Brave Search API Key**: Get from [Brave Search API](https://brave.com/search/api/)

**Set up environment (optional - can be in config file):**
```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export BRAVE_API_KEY="your-brave-search-key"
```

## Usage

### 1. Start Required Services

**Start Neo4j (if using Docker):**
```bash
# Start Neo4j container
docker start neo4j-trading

# Or run if not created yet
docker run --name neo4j-trading \
    -p 7474:7474 -p 7687:7687 \
    -d \
    -e NEO4J_AUTH=neo4j/password \
    -e NEO4J_PLUGINS='["apoc"]' \
    neo4j:latest
```

**Start IBKR Connection:**
1. Launch IB Gateway or TWS
2. Log in with your account credentials
3. Ensure API settings are configured (see Prerequisites)
4. Keep the application running

### 2. Run the Enhanced Trading Agent
```bash
# Activate virtual environment
source .venv/bin/activate

# Run the agent
uv run fs_agent.py interactive
```

### 3. New Enhanced Features

**Automatic Error Handling:**
- The system now includes retry logic with exponential backoff
- API overload errors are handled gracefully
- Automatic context reset to prevent token limit issues

**Graph Database Analysis:**
- Create relationship networks between stocks, sectors, and market participants
- Analyze portfolio connections and correlations
- Identify market clusters and patterns

**Enhanced Search Capabilities:**
- DuckDuckGo integration for comprehensive web research
- Cross-referencing multiple data sources
- Citation-backed research reports

**Quantitative Optimization:**
- Advanced portfolio optimization algorithms
- Risk-adjusted return calculations  
- Multi-objective optimization strategies

## Agent Usage Examples

### Basic Queries (Router automatically selects best agent):
```
Analyze AAPL stock performance and create Python visualizations
What's my current portfolio performance?
Should I buy Tesla stock right now?
Create a Python backtest for a momentum strategy
Get the latest news about the semiconductor sector
Calculate the Sharpe ratio for my current positions
```

### Neo4j Graph Analysis:
```
@neo4j_analyst Create a network of tech stocks and their relationships
@neo4j_analyst Analyze portfolio correlations using graph database
@neo4j_analyst Find clusters in the S&P 500 by sector relationships
```

### Research Analysis:
```
@research_analyst Comprehensive analysis of renewable energy sector
@research_analyst Cross-reference multiple sources on Fed policy impact
@research_analyst Build a research report on emerging market trends
```

### Python Analytics:
```
@python_analyst Create a Monte Carlo simulation for portfolio returns
@python_analyst Backtest a mean reversion strategy using pandas
@python_analyst Build a correlation heatmap of my current positions
```

### Manual Agent Selection:
```
@financial_analyst analyze MSFT trends with web research
@python_analyst create advanced technical indicators
@trading_advisor recommend entry points for QQQ with stop losses
@portfolio_manager suggest rebalancing with risk constraints
```

## New Troubleshooting Section

### Docker-Related Issues

**Neo4j Connection Problems:**
```bash
# Check if Neo4j container is running
docker ps | grep neo4j

# Check Neo4j logs
docker logs neo4j-trading

# Restart Neo4j container
docker restart neo4j-trading
```

**Docker Permission Issues:**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Then log out and back in
```

### Enhanced Error Handling
The system now automatically handles:
- API overload with retry logic
- Context length limits with automatic reset
- Network timeouts with graceful degradation
- Docker container startup delays

**Common Error Messages:**
- "API overloaded": System will retry automatically
- "Context too long": Router will reset and continue
- "Container not found": Check Docker installation and image pulls

### Performance Optimization
- Use `@fast` model alias for quick responses
- Use `@powerful` model alias for complex analysis
- Break large queries into smaller chunks
- Monitor Docker resource usage: `docker stats`

## Advanced Configuration

### Custom Neo4j Setup
For production use, configure Neo4j with persistent storage:

```bash
docker run --name neo4j-trading \
    -p 7474:7474 -p 7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -e NEO4J_AUTH=neo4j/your_secure_password \
    -e NEO4J_PLUGINS='["apoc","graph-data-science"]' \
    neo4j:latest
```

### Model Performance Tuning
Adjust model settings in config for different use cases:

```yaml
# For high-frequency trading (fast responses)
trading_advisor:
  model: "fast"
  temperature: 0.1

# For research analysis (detailed responses)  
research_analyst:
  model: "powerful"
  temperature: 0.3
```

## Project Structure
```
ibkr-trading-agent/
├── fs_agent.py                 # Enhanced main agent application
├── ibkr_fast_mcp_server.py    # IBKR MCP server
├── brave_mcp_server.py        # Brave search server
├── quant_optimization_mcp.py  # NEW: Quantitative optimization server
├── fastagent.config.yaml      # Enhanced configuration
├── requirements.txt           # Updated dependencies
├── .venv/                     # Virtual environment
├── docker-compose.yml         # Optional: Docker services setup
└── README.md                  # This enhanced file
```

## Security Notes
- Use paper trading accounts for testing
- Never commit API keys to version control
- Keep IB Gateway/TWS updated
- Monitor your positions and orders carefully
- The system can execute real trades if using live accounts
- Secure your Neo4j database with strong passwords
- Review Docker container security settings

## API Rate Limits
- **Anthropic**: Varies by plan (enhanced retry logic included)
- **IBKR**: ~50 requests per second (automatic throttling)
- **Brave Search**: Varies by plan
- **DuckDuckGo**: Rate limited by service
- **Neo4j**: Local database, no external limits

## What's New in v2.0
- ✅ **Neo4j Graph Database Integration** - Relationship and network analysis
- ✅ **DuckDuckGo Search Integration** - Enhanced web research capabilities  
- ✅ **Quantitative Optimization Server** - Advanced portfolio optimization
- ✅ **Enhanced Error Handling** - Retry logic with exponential backoff
- ✅ **Model Aliases** - Fast/Balanced/Powerful model selection
- ✅ **Elicitation Support** - Interactive prompting capabilities
- ✅ **Docker Integration** - Containerized services for scalability
- ✅ **Multi-Source Research** - Cross-referencing capabilities
- ✅ **Improved Context Management** - Automatic reset to prevent overload

## Support
For issues:
1. Check IBKR connection and API settings
2. Verify all dependencies are installed  
3. Ensure Docker containers are running
4. Check Neo4j database connectivity
5. Review logs for specific error messages
6. Ensure API keys are valid and have sufficient credits
7. Monitor Docker resource usage

## License
This project is for educational and personal use. Ensure compliance with:
- Interactive Brokers API terms
- Anthropic API terms
- Brave Search API terms
- Neo4j Community License
- Docker terms of service

**Disclaimer**: This software is for educational purposes. Trading involves risk. Always verify trades and use appropriate risk management. The enhanced features provide more analytical power but do not guarantee trading success.