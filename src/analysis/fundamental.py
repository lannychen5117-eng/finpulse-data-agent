from typing import Dict, Any

def analyze_fundamentals(info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes fundamental data and returns key metrics with a simple assessment.
    """
    if not info:
        return {}
    
    # Extract key metrics with defaults
    pe_ratio = info.get('trailingPE')
    forward_pe = info.get('forwardPE')
    peg_ratio = info.get('pegRatio')
    market_cap = info.get('marketCap')
    revenue_growth = info.get('revenueGrowth')
    profit_margins = info.get('profitMargins')
    debt_to_equity = info.get('debtToEquity')
    
    analysis = {
        "metrics": {
            "P/E": pe_ratio,
            "Forward P/E": forward_pe,
            "PEG": peg_ratio,
            "Revenue Growth": revenue_growth,
            "Profit Margins": profit_margins,
            "Debt/Equity": debt_to_equity
        },
        "signals": []
    }
    
    # Simple rule-based signals (just for initial interpretation)
    signals = []
    if pe_ratio and pe_ratio < 15:
        signals.append("Undervalued based on P/E (< 15)")
    elif pe_ratio and pe_ratio > 50:
        signals.append("Potentially overvalued based on P/E (> 50)")
        
    if peg_ratio and peg_ratio < 1.0:
        signals.append("Undervalued based on PEG (< 1.0)")
        
    if revenue_growth and revenue_growth > 0.20:
        signals.append("High Growth (> 20% revenue growth)")
        
    analysis["signals"] = signals
    
    return analysis
