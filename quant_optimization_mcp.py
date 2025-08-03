#!/usr/bin/env python3
"""
Quantum Portfolio Optimization MCP Server using FastMCP
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np

from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("Quantum Portfolio Optimizer")

# Import quantum libraries with version compatibility
QUANTUM_AVAILABLE = False
try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    
    # Try different Sampler imports for version compatibility
    try:
        from qiskit.primitives import Sampler
    except ImportError:
        try:
            from qiskit_aer.primitives import Sampler
        except ImportError:
            # Fallback - we'll use simulator directly
            Sampler = None
    
    QUANTUM_AVAILABLE = True
    logger.info("✅ Quantum libraries loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Quantum libraries not available: {e}")

@mcp.tool()
async def check_quantum_status() -> Dict[str, Any]:
    """Check quantum computing status"""
    return {
        "quantum_available": QUANTUM_AVAILABLE,
        "sampler_available": Sampler is not None if QUANTUM_AVAILABLE else False,
        "message": "Quantum optimization ready!" if QUANTUM_AVAILABLE else "Quantum libraries missing",
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
async def quantum_random_numbers(num_bits: int = 4, num_samples: int = 10) -> Dict[str, Any]:
    """Generate quantum random numbers using superposition"""
    if not QUANTUM_AVAILABLE:
        return {"error": "Quantum libraries not available"}
    
    try:
        # Create quantum circuit
        qc = QuantumCircuit(num_bits, num_bits)
        
        # Apply Hadamard gates for superposition
        for i in range(num_bits):
            qc.h(i)
        
        # Measure all qubits
        qc.measure_all()
        
        # Execute on simulator
        simulator = AerSimulator()
        job = simulator.run(qc, shots=num_samples)
        result = job.result().get_counts()
        
        # Convert to decimal numbers
        random_numbers = []
        for binary_string, count in result.items():
            decimal_value = int(binary_string.replace(' ', ''), 2)
            random_numbers.extend([decimal_value] * count)
        
        return {
            "random_numbers": random_numbers[:num_samples],
            "max_value": 2**num_bits - 1,
            "num_unique_outcomes": len(result),
            "method": "quantum_superposition",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def simple_portfolio_optimization(
    symbols: List[str],
    expected_returns: List[float],
    risk_weights: List[float] = None
) -> Dict[str, Any]:
    """Simple portfolio optimization (classical approach)"""
    try:
        if len(symbols) != len(expected_returns):
            return {"error": "Symbols and returns length mismatch"}
        
        if risk_weights and len(risk_weights) != len(symbols):
            return {"error": "Risk weights length mismatch"}
        
        # Simple optimization: select top performers with risk adjustment
        if not risk_weights:
            risk_weights = [1.0] * len(symbols)  # Equal risk if not provided
        
        # Calculate risk-adjusted returns
        risk_adjusted_returns = [
            ret / risk for ret, risk in zip(expected_returns, risk_weights)
        ]
        
        # Select top 3-4 assets based on risk-adjusted returns
        asset_scores = list(zip(symbols, expected_returns, risk_adjusted_returns, risk_weights))
        asset_scores.sort(key=lambda x: x[2], reverse=True)  # Sort by risk-adjusted return
        
        # Select top 3 assets
        selected_assets = asset_scores[:3]
        
        return {
            "method": "simple_risk_adjusted",
            "selected_assets": [asset[0] for asset in selected_assets],
            "asset_analysis": [
                {
                    "symbol": asset[0],
                    "expected_return": asset[1],
                    "risk_adjusted_return": asset[2],
                    "risk_weight": asset[3]
                } for asset in selected_assets
            ],
            "quantum_available": QUANTUM_AVAILABLE,
            "recommendation": "Equal weight allocation among selected assets",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def monte_carlo_portfolio_simulation(
    initial_value: float,
    num_scenarios: int = 100,
    time_horizon_days: int = 30
) -> Dict[str, Any]:
    """Monte Carlo portfolio simulation with quantum randomness"""
    try:
        if not QUANTUM_AVAILABLE:
            # Fallback to numpy random
            import numpy as np
            random_source = "numpy_pseudorandom"
            random_numbers = np.random.rand(num_scenarios * time_horizon_days)
        else:
            # Use quantum randomness
            quantum_randoms = await quantum_random_numbers(
                num_bits=8, 
                num_samples=num_scenarios * time_horizon_days
            )
            
            if "error" in quantum_randoms:
                return quantum_randoms
            
            random_source = "quantum_superposition"
            # Normalize to [0,1]
            random_numbers = np.array(quantum_randoms['random_numbers']) / 255.0
        
        # Market simulation parameters
        daily_return_mean = 0.0003  # ~8% annual
        daily_return_std = 0.015    # ~24% annual volatility
        
        # Run Monte Carlo simulation
        final_values = []
        
        for scenario in range(num_scenarios):
            portfolio_value = initial_value
            
            # Simulate daily returns
            start_idx = scenario * time_horizon_days
            scenario_randoms = random_numbers[start_idx:start_idx + time_horizon_days]
            
            for rand_val in scenario_randoms:
                # Convert uniform random to normal distribution (Box-Muller approximation)
                normal_random = np.sqrt(-2 * np.log(rand_val + 0.0001)) * np.cos(2 * np.pi * rand_val)
                daily_return = daily_return_mean + daily_return_std * normal_random
                portfolio_value *= (1 + daily_return)
            
            final_values.append(portfolio_value)
        
        # Calculate risk metrics
        final_values = np.array(final_values)
        returns = (final_values - initial_value) / initial_value
        
        var_95 = np.percentile(final_values, 5)
        var_99 = np.percentile(final_values, 1)
        
        return {
            "simulation_results": {
                "initial_value": initial_value,
                "scenarios": num_scenarios,
                "time_horizon_days": time_horizon_days,
                "expected_value": float(np.mean(final_values)),
                "median_value": float(np.median(final_values)),
                "min_value": float(np.min(final_values)),
                "max_value": float(np.max(final_values)),
                "standard_deviation": float(np.std(final_values))
            },
            "risk_metrics": {
                "value_at_risk_95": float(var_95),
                "value_at_risk_99": float(var_99),
                "probability_of_loss": float(np.sum(final_values < initial_value) / len(final_values)),
                "expected_return": float(np.mean(returns)),
                "return_volatility": float(np.std(returns))
            },
            "randomness_source": random_source,
            "quantum_available": QUANTUM_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    logger.info("🚀 Starting Quantum Portfolio Optimization MCP Server...")
    mcp.run()