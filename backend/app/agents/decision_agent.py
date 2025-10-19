"""Decision agent that generates dual recommendations (AI + User personalized)."""
from typing import Dict, List, Tuple
from app.agents.state import AgentState
from app.services.llm_service import get_llm_service


def decision_agent(state: AgentState) -> Dict:
    """
    Decision agent that generates two recommendations:
    1. AI's independent analysis (unbiased, purely data-driven)
    2. User's personalized recommendation (adapted to their investment style)
    """
    symbol = state["symbol"]
    investment_style = state["investment_style"]
    
    try:
        print(f"🎯 Decision Agent: Starting dual recommendation generation for {symbol}")
        print(f"👤 Decision Agent: User style = {investment_style}")
        
        # Build comprehensive context from all agents
        print(f"📊 Decision Agent: Building context from all agent outputs...")
        context = build_decision_context(state)
        
        llm = get_llm_service()
        
        # Generate AI's independent recommendation
        print(f"🤖 Decision Agent: Generating AI's independent recommendation...")
        ai_rec = generate_ai_recommendation(llm, symbol, context)
        print(f"✓ Decision Agent: AI recommendation = {ai_rec['action']} ({ai_rec['confidence']:.0%} confidence)")
        
        # Generate user's personalized recommendation
        print(f"👤 Decision Agent: Generating user's personalized recommendation...")
        user_rec = generate_user_recommendation(llm, symbol, context, investment_style)
        print(f"✓ Decision Agent: User recommendation = {user_rec['action']} ({user_rec['confidence']:.0%} confidence)")
        
        # Generate comparison insight
        print(f"🔍 Decision Agent: Generating comparison insight...")
        comparison = generate_comparison(llm, ai_rec, user_rec, investment_style)
        print(f"✅ Decision Agent: Dual recommendations complete for {symbol}")
    except Exception as e:
        print(f"❌ Decision Agent ERROR: Failed during recommendation generation - {str(e)}")
        raise
    
    return {
        # AI recommendation
        "ai_recommendation": ai_rec['action'],
        "ai_confidence": ai_rec['confidence'],
        "ai_horizon": ai_rec['horizon'],
        "ai_key_reasons": ai_rec['key_reasons'],
        "ai_reasoning": ai_rec['reasoning'],
        "ai_macro_impact": ai_rec.get('macro_impact', ''),
        "ai_weights": ai_rec['weights'],
        "ai_technical_signals": ai_rec['technical_signals'],
        "ai_entry_price": ai_rec.get('entry_price'),
        "ai_targets": ai_rec.get('targets'),
        "ai_stop_loss": ai_rec.get('stop_loss'),
        "ai_entry_price_strategy": ai_rec.get('entry_price_strategy', ''),
        "ai_reassessment_timeline": ai_rec.get('reassessment_timeline', ''),
        "ai_target_strategy": ai_rec.get('target_strategy', ''),
        
        # User recommendation
        "user_recommendation": user_rec['action'],
        "user_confidence": user_rec['confidence'],
        "user_horizon": user_rec['horizon'],
        "user_key_reasons": user_rec['key_reasons'],
        "user_reasoning": user_rec['reasoning'],
        "user_macro_impact": user_rec.get('macro_impact', ''),
        "user_weights": user_rec['weights'],
        "user_technical_signals": user_rec['technical_signals'],
        "user_entry_price": user_rec.get('entry_price'),
        "user_targets": user_rec.get('targets'),
        "user_stop_loss": user_rec.get('stop_loss'),
        "user_entry_price_strategy": user_rec.get('entry_price_strategy', ''),
        "user_reassessment_timeline": user_rec.get('reassessment_timeline', ''),
        "user_target_strategy": user_rec.get('target_strategy', ''),
        
        # Comparison
        "comparison_insight": comparison,
    }


def build_decision_context(state: AgentState) -> str:
    """Build comprehensive context from all agent outputs."""
    technical = state.get("technical_signals", {})
    indicators = state.get("technical_indicators", {})
    
    context = f"""
STOCK: {state['symbol']}
CURRENT PRICE: ${indicators.get('price', 0):.2f}

=== FUNDAMENTAL RESEARCH ===
{state.get('company_info', 'No research data available')}

Financial Metrics:
- Market Cap: ${state.get('financial_data', {}).get('market_cap', 0):,.0f}
- P/E Ratio: {state.get('financial_data', {}).get('pe_ratio', 0):.2f}
- Revenue Growth: {state.get('financial_data', {}).get('revenue_growth', 0):.2%}
- Profit Margin: {state.get('financial_data', {}).get('profit_margin', 0):.2%}

=== TECHNICAL ANALYSIS ===
Trend: {technical.get('long_term_trend', 'N/A')}
MA Crossover: {technical.get('ma_crossover', 'N/A')}
Overall Signal: {technical.get('overall', 'N/A')}

Key Indicators:
- SMA(20): ${indicators.get('sma_20', 0):.2f}
- SMA(50): ${indicators.get('sma_50', 0):.2f}
- SMA(200): ${indicators.get('sma_200', 0):.2f}
- RSI(14): {indicators.get('rsi', 0):.1f} - {technical.get('rsi_signal', 'N/A')}
- MACD: {technical.get('macd_signal', 'N/A')}
- Volume: {'High' if indicators.get('volume', 0) > indicators.get('volume_avg', 0) * 1.2 else 'Normal'}

Support/Resistance:
- Support: ${indicators.get('support', 0):.2f}
- Resistance: ${indicators.get('resistance', 0):.2f}

=== SENTIMENT ANALYSIS ===
{state.get('news_summary', 'No sentiment data available')}

Sentiment Score: {state.get('sentiment_score', 0):.2f} (-1 = very negative, +1 = very positive)

=== MACROECONOMIC ENVIRONMENT ===
{state.get('macro_summary', 'No macro data available')}

Key Macro Indicators:
- VIX (Market Volatility): {state.get('macro_indicators', {}).get('vix', 'N/A')}
- Federal Funds Rate: {state.get('macro_indicators', {}).get('fed_rate', 'N/A')}%
- GDP Growth: {state.get('macro_indicators', {}).get('gdp_growth', 'N/A')}%
- CPI Inflation: {state.get('macro_indicators', {}).get('inflation_cpi', 'N/A')}%
- Unemployment Rate: {state.get('macro_indicators', {}).get('unemployment', 'N/A')}%
- Overall Market Risk Level: {state.get('macro_risk_level', 'medium').upper()}
"""
    return context


def generate_ai_recommendation(llm, symbol: str, context: str) -> Dict:
    """Generate AI's independent, unbiased recommendation."""
    
    system_prompt = """You are an expert stock analyst providing an objective, data-driven recommendation.

Analyze the stock independently and determine:
1. Is this better suited for LONG-TERM investing (2-5 years), MEDIUM-TERM investing (3-12 months), or SHORT-TERM trading (weeks to 3 months)?
2. What should be the weighting of each factor? (fundamentals, technicals, sentiment, macro)
3. What is the recommendation? (BUY, HOLD, or SELL)
4. What is your confidence level? (0.0 to 1.0)

⚠️ IMPORTANT: You MUST explicitly consider and cite the macroeconomic indicators (VIX, Fed Rate, GDP, CPI, Unemployment) in your analysis. Explain how the current macro environment affects this stock.

RECOMMENDATION INTERPRETATION:
- BUY: Buy this stock (if you don't own) or add to position (if you own)
- HOLD: Wait for better entry (if you don't own) or keep current position (if you own)
- SELL: Don't buy this stock (if you don't own) or exit position (if you own)

Provide your analysis in this EXACT format:

RECOMMENDATION: [BUY/HOLD/SELL]
CONFIDENCE: [0.0-1.0]
HORIZON: [specific timeframe like "2-5 years", "6-9 months", or "4-8 weeks"]
WEIGHTS: Fundamentals=[0.0-1.0], Technical=[0.0-1.0], Sentiment=[0.0-1.0], Macro=[0.0-1.0]

KEY REASONS:
- [Reason 1 - must include at least one macro factor]
- [Reason 2]
- [Reason 3]
- [Reason 4]

MACRO IMPACT:
[1-2 sentences on how VIX, Fed rates, inflation, GDP, or unemployment specifically affect this investment decision and timing]

Example: "Current low VIX at 15.2 and stable Fed rates at 5.25% support risk-on sentiment, while 2.1% inflation suggests moderate economic growth that favors growth stocks like this one."

ENTRY PRICE: $[price] (should be close to current price)
TARGET PRICES: $[price1], $[price2] (realistic upside targets based on technical analysis, support/resistance levels, and fundamental valuation - must be higher than entry price)
STOP LOSS: $[price] (risk management level below entry price)

ENTRY PRICE STRATEGY:
- If current price < entry price: Buy immediately
- If current price > entry price: [specific strategy based on horizon]
- Maximum wait time: [specific timeframe]
- If not reached in time: [specific action]

REASSESSMENT TIMELINE:
- [timeframe1]: [specific checkpoint and action]
- [timeframe2]: [specific checkpoint and action]
- [timeframe3]: [specific checkpoint and action]

TARGET STRATEGY:
- First target: Take [percentage]% profits, let remainder run
- Second target: [specific strategy]
- Exit triggers: [specific conditions]

IMPORTANT TARGET PRICE GUIDELINES:
- Use the current price and technical analysis (support/resistance levels, moving averages) to set realistic targets
- Consider the investment horizon: short-term (weeks) = smaller targets, long-term (years) = larger targets
- Target prices should be based on technical levels, not arbitrary numbers
- For example: if current price is $100, targets might be $105 (short-term), $120 (medium-term), $150 (long-term)

REASONING:
- Decision Rationale: [explain why this specific recommendation (BUY/HOLD/SELL) makes sense]
- Weighting Justification: [explain why you chose these specific weights for fundamentals, technical, sentiment, macro]
- Horizon Logic: [explain why this timeframe (short/medium/long-term) is appropriate]
- Macro Environment Impact: [explain HOW the macroeconomic environment influenced this recommendation - cite specific indicators]

Example:
- Decision Rationale: This BUY recommendation is based on strong fundamentals showing 22% revenue growth and 15% profit margins, combined with bullish technical indicators including golden cross and RSI at 45.
- Weighting Justification: Fundamentals get 40% weight due to strong financials, technical gets 30% for bullish signals, macro gets 20% for supportive environment, sentiment gets 10% as it's neutral.
- Horizon Logic: The 2-5 year horizon allows for full realization of the company's AI transformation strategy while managing near-term volatility risks.
- Macro Environment Impact: Current macro environment with VIX at 18.5 and Fed rates at 5.25% supports growth stocks, while 2.1% inflation suggests moderate economic growth that favors this sector.

TECHNICAL SIGNALS:
- SMA Analysis: [interpretation]
- RSI: [interpretation]
- MACD: [interpretation]
- Volume: [interpretation]

Example:
- SMA Analysis: Price above all major moving averages, bullish trend confirmed
- RSI: 45, showing momentum but not overbought, room for upside
- MACD: Bullish crossover, positive momentum building
- Volume: Above average, confirming breakout with institutional interest"""

    response = llm.invoke(system_prompt, f"Analyze {symbol}:\n\n{context}")
    print(f"🤖 AI Recommendation LLM Response:\n{response}\n{'='*50}")
    
    return parse_recommendation(response)


def generate_user_recommendation(llm, symbol: str, context: str, style: str) -> Dict:
    """Generate user's personalized recommendation based on investment style."""
    
    style_descriptions = {
        "conservative": "long-term, risk-averse, focused on fundamentals and capital preservation",
        "balanced": "moderate risk, balanced timeframe, considering all factors equally",
        "aggressive": "short-term trading, risk-tolerant, focused on momentum and technical signals",
    }
    
    style_desc = style_descriptions.get(style, style_descriptions["balanced"])
    
    # Define style-specific timeframes and strategies
    style_configs = {
        "conservative": {
            "horizon_range": "1-5 years",
            "entry_wait": "6-12 months",
            "reassessment": "quarterly",
            "target_strategy": "Take 25% profits at first target, let remainder run"
        },
        "balanced": {
            "horizon_range": "3-12 months", 
            "entry_wait": "1-3 months",
            "reassessment": "monthly",
            "target_strategy": "Take 50% profits at first target, let remainder run"
        },
        "aggressive": {
            "horizon_range": "weeks to 3 months",
            "entry_wait": "1-2 weeks", 
            "reassessment": "weekly",
            "target_strategy": "Take 75% profits at first target, quick exit"
        }
    }
    
    config = style_configs.get(style, style_configs["balanced"])
    
    system_prompt = f"""You are a personalized investment advisor. The user has a {style.upper()} investment style: {style_desc}.

Tailor your recommendation to match their style:
- Conservative: Prioritize fundamentals (40-50%), macro considerations (20-30%), longer horizons (1-5 years), lower risk
- Balanced: Equal weighting across all factors including macro, medium horizons (3-12 months)
- Aggressive: Prioritize technicals (40-50%), but still consider macro risks (10-15%), shorter horizons (weeks-months), capture momentum

⚠️ IMPORTANT: You MUST explicitly consider how the macroeconomic environment (VIX, Fed Rate, GDP, CPI, Unemployment) aligns with or conflicts with this user's investment style.

RECOMMENDATION INTERPRETATION:
- BUY: Buy this stock (if you don't own) or add to position (if you own)
- HOLD: Wait for better entry (if you don't own) or keep current position (if you own)
- SELL: Don't buy this stock (if you don't own) or exit position (if you own)

Provide your analysis in this EXACT format:

RECOMMENDATION: [BUY/HOLD/SELL]
CONFIDENCE: [0.0-1.0]
HORIZON: [specific timeframe matching {style} style: {config['horizon_range']}]
WEIGHTS: Fundamentals=[0.0-1.0], Technical=[0.0-1.0], Sentiment=[0.0-1.0], Macro=[0.0-1.0]

KEY REASONS:
- [Reason 1 - relevant to {style} style, include macro if significant]
- [Reason 2]
- [Reason 3]
- [Reason 4]

MACRO IMPACT:
[1-2 sentences on how the current macro environment (cite specific indicators) affects this recommendation for a {style} investor]

Example: "For a {style} investor, the current macro environment with VIX at 18.5 and Fed rates at 5.25% [supports/requires caution for] this investment strategy, as [explain specific impact on {style} style]."

ENTRY PRICE: $[price] (should be close to current price)
TARGET PRICES: $[price1], $[price2] (realistic upside targets based on technical analysis, support/resistance levels, and fundamental valuation - must be higher than entry price)
STOP LOSS: $[price] (risk management level below entry price)

ENTRY PRICE STRATEGY:
- If current price < entry price: Buy immediately
- If current price > entry price: [specific strategy for {style} style]
- Maximum wait time: {config['entry_wait']}
- If not reached in time: [specific action for {style} investor]

REASSESSMENT TIMELINE:
- [timeframe1]: [specific checkpoint for {style} style]
- [timeframe2]: [specific checkpoint for {style} style]
- [timeframe3]: [specific checkpoint for {style} style]

TARGET STRATEGY:
- First target: {config['target_strategy']}
- Second target: [specific strategy for {style} style]
- Exit triggers: [specific conditions for {style} style]

IMPORTANT TARGET PRICE GUIDELINES:
- Use the current price and technical analysis (support/resistance levels, moving averages) to set realistic targets
- Consider the investment horizon: short-term (weeks) = smaller targets, long-term (years) = larger targets
- Target prices should be based on technical levels, not arbitrary numbers
- For example: if current price is $100, targets might be $105 (short-term), $120 (medium-term), $150 (long-term)

REASONING:
- Style Alignment: [explain why this recommendation fits the {style} investment style]
- Weighting Justification: [explain how you weighted the factors to match {style} risk tolerance and preferences]
- Trade Plan: [explain the specific trade/investment plan for a {style} investor]
- Macro Impact: [explain how macro conditions support or challenge this strategy for a {style} investor]

Example:
- Style Alignment: This recommendation aligns with {style} investment principles by [explain how it matches {style} risk tolerance and time horizon].
- Weighting Justification: [Explain specific weightings that match {style} style - e.g., conservative gets higher macro weight, aggressive gets higher technical weight].
- Trade Plan: [Specific entry/exit strategy tailored to {style} investor - position sizing, risk management, etc.].
- Macro Impact: The macro environment [supports/challenges] this approach for {style} investors because [specific macro factors and their impact on {style} strategy].

TECHNICAL SIGNALS:
- SMA Analysis: [interpretation for {style} trader]
- RSI: [interpretation]
- MACD: [interpretation]
- Volume: [interpretation]

Example:
- SMA Analysis: [interpretation relevant to {style} trading style]
- RSI: [interpretation with {style} risk tolerance]
- MACD: [interpretation for {style} timeframe]
- Volume: [interpretation for {style} position sizing]"""

    response = llm.invoke(system_prompt, f"Analyze {symbol} for a {style} investor:\n\n{context}")
    print(f"🤖 User ({style}) Recommendation LLM Response:\n{response}\n{'='*50}")
    
    return parse_recommendation(response)


def generate_comparison(llm, ai_rec: Dict, user_rec: Dict, style: str) -> str:
    """Generate insight comparing AI and user recommendations."""
    
    comparison_context = f"""
AI Recommendation: {ai_rec['action']} (Confidence: {ai_rec['confidence']:.0%}, Horizon: {ai_rec['horizon']})
User Recommendation ({style}): {user_rec['action']} (Confidence: {user_rec['confidence']:.0%}, Horizon: {user_rec['horizon']})

AI Reasoning: {ai_rec['reasoning'][:200]}...
User Reasoning: {user_rec['reasoning'][:200]}...
"""
    
    system_prompt = """Compare these two recommendations and provide a brief insight (2-3 sentences) about:
1. Do they agree or disagree?
2. Why might they differ?
3. What should the investor consider?

Keep it concise and actionable."""
    
    return llm.invoke(system_prompt, comparison_context)


def parse_recommendation(text: str) -> Dict:
    """Parse LLM response into structured recommendation."""
    import re
    
    rec = {
        'action': 'HOLD',
        'confidence': 0.5,
        'horizon': 'Medium-term',
        'key_reasons': [],
        'reasoning': '',
        'macro_impact': '',
        'weights': {'fundamental': 0.25, 'technical': 0.25, 'sentiment': 0.25, 'macro': 0.25},
        'technical_signals': {},
        'entry_price': None,
        'targets': None,
        'stop_loss': None,
        'entry_price_strategy': '',
        'reassessment_timeline': '',
        'target_strategy': '',
    }
    
    # Extract recommendation
    rec_match = re.search(r'RECOMMENDATION:\s*(BUY|HOLD|SELL)', text, re.IGNORECASE)
    if rec_match:
        rec['action'] = rec_match.group(1).upper()
    
    # Extract confidence
    conf_match = re.search(r'CONFIDENCE:\s*([0-9.]+)', text)
    if conf_match:
        rec['confidence'] = float(conf_match.group(1))
    
    # Extract horizon
    horizon_match = re.search(r'HORIZON:\s*([^\n]+)', text)
    if horizon_match:
        rec['horizon'] = horizon_match.group(1).strip()
    
    # Extract weights (now with macro)
    weights_match = re.search(r'WEIGHTS:\s*Fundamentals?=([0-9.]+).*Technical=([0-9.]+).*Sentiment=([0-9.]+).*Macro=([0-9.]+)', text, re.IGNORECASE)
    if weights_match:
        rec['weights'] = {
            'fundamental': float(weights_match.group(1)),
            'technical': float(weights_match.group(2)),
            'sentiment': float(weights_match.group(3)),
            'macro': float(weights_match.group(4)),
        }
    else:
        # Fallback: try without macro (for backwards compatibility)
        weights_match_old = re.search(r'WEIGHTS:\s*Fundamentals?=([0-9.]+).*Technical=([0-9.]+).*Sentiment=([0-9.]+)', text, re.IGNORECASE)
        if weights_match_old:
            rec['weights'] = {
                'fundamental': float(weights_match_old.group(1)),
                'technical': float(weights_match_old.group(2)),
                'sentiment': float(weights_match_old.group(3)),
                'macro': 0.0,
            }
    
    # Extract key reasons
    reasons_section = re.search(r'KEY REASONS:(.*?)(?=MACRO IMPACT:|ENTRY PRICE:|TARGET PRICES:|REASONING:|$)', text, re.DOTALL)
    if reasons_section:
        reasons_text = reasons_section.group(1)
        # Try multiple formats: single dash, double dash, and asterisk
        reasons = [r.strip('- ').strip() for r in reasons_text.split('\n') if r.strip().startswith('-')]
        if not reasons:
            # Fallback: try double dash format
            reasons = [r.strip('-- ').strip() for r in reasons_text.split('\n') if r.strip().startswith('--')]
        if not reasons:
            # Fallback: try asterisk format (AI often uses this)
            reasons = [r.strip('* ').strip() for r in reasons_text.split('\n') if r.strip().startswith('*')]
        rec['key_reasons'] = [r for r in reasons if r][:4]  # Max 4 reasons
        print(f"✓ Extracted key reasons: {rec['key_reasons']}")
    else:
        print(f"⚠️ No key reasons found in LLM response")
    
    # Extract macro impact
    macro_impact_match = re.search(r'MACRO IMPACT:(.*?)(?=ENTRY PRICE:|TARGET PRICES:|REASONING:|$)', text, re.DOTALL)
    if macro_impact_match:
        rec['macro_impact'] = macro_impact_match.group(1).strip()
    
    # Extract entry price
    entry_match = re.search(r'ENTRY PRICE:\s*\$?([0-9.]+)', text)
    if entry_match:
        rec['entry_price'] = float(entry_match.group(1))
        print(f"✓ Extracted entry price: ${rec['entry_price']:.2f}")
    else:
        print(f"⚠️ No entry price found in LLM response")
    
    # Extract target prices with timeframes
    targets_match = re.search(r'TARGET PRICES?:\s*([^\n]+)', text)
    if targets_match:
        targets_text = targets_match.group(1)
        # Extract multiple target prices from text like "$459.00 (3 years), $490.00 (5 years)"
        # Look for patterns like $459.00, $1,050.00, etc. - but exclude timeframes in parentheses
        price_pattern = r'\$([0-9,]+\.?[0-9]*)'
        prices = re.findall(price_pattern, targets_text)
        
        # Also try to find prices without $ sign but exclude timeframes
        # Look for numbers that are likely prices (not in parentheses and reasonable values)
        fallback_pattern = r'(?<!\()\b([0-9,]+\.?[0-9]*)\b(?!\s*(?:years?|months?|weeks?|days?|hours?|minutes?))'
        fallback_prices = re.findall(fallback_pattern, targets_text)
        
        # Combine both approaches
        all_prices = prices + fallback_prices
        
        # Convert all extracted prices to floats (remove commas first)
        targets = [float(p.replace(',', '')) for p in all_prices]
        
        # Remove duplicates while preserving order
        seen = set()
        targets = [x for x in targets if not (x in seen or seen.add(x))]
        
        rec['targets'] = targets[:3]  # Max 3 targets
        print(f"✓ Extracted target prices: {rec['targets']}")
    else:
        print(f"⚠️ No target prices found in LLM response")
    
    # Final validation: Ensure target prices are reasonable
    if rec.get('targets') and rec.get('entry_price'):
        entry_price = rec['entry_price']
        validated_targets = []
        for target in rec['targets']:
            # Target should be higher than entry price (at least 0.5% higher for very short-term trades) and not more than 10x entry price
            if target > entry_price * 1.005 and target < entry_price * 10:
                validated_targets.append(target)
            else:
                print(f"⚠️ Filtered out unrealistic target price: ${target:.2f} (entry: ${entry_price:.2f}) - must be > ${entry_price * 1.005:.2f} and < ${entry_price * 10:.2f}")
        rec['targets'] = validated_targets
    
    # Fallback: If no targets found in TARGET PRICES section, try to extract from reasoning
    if not rec['targets'] or len(rec['targets']) < 2:
        # Look for target prices mentioned in reasoning text
        reasoning_text = rec.get('reasoning', '')
        if reasoning_text:
            # Look for patterns like "targeting $459-$490" or "target $459, $490"
            reasoning_targets = re.findall(r'target(?:ing)?\s*\$?([0-9,]+\.?[0-9]*)(?:[-\s]*\$?([0-9,]+\.?[0-9]*))?', reasoning_text, re.IGNORECASE)
            if reasoning_targets:
                targets = []
                for match in reasoning_targets:
                    for price_str in match:
                        if price_str:
                            targets.append(float(price_str.replace(',', '')))
                if targets:
                    # Remove duplicates while preserving order
                    seen = set()
                    targets = [x for x in targets if not (x in seen or seen.add(x))]
                    rec['targets'] = targets[:3]
                    print(f"✓ Extracted fallback target prices: {rec['targets']}")
    
    # Extract stop loss
    stop_match = re.search(r'STOP LOSS:\s*\$?([0-9.]+)', text)
    if stop_match:
        rec['stop_loss'] = float(stop_match.group(1))
    
    # Extract entry price strategy
    entry_strategy_match = re.search(r'ENTRY PRICE STRATEGY:(.*?)(?=REASSESSMENT TIMELINE:|TARGET STRATEGY:|REASONING:|$)', text, re.DOTALL)
    if entry_strategy_match:
        rec['entry_price_strategy'] = entry_strategy_match.group(1).strip()
    
    # Extract reassessment timeline
    reassessment_match = re.search(r'REASSESSMENT TIMELINE:(.*?)(?=TARGET STRATEGY:|REASONING:|$)', text, re.DOTALL)
    if reassessment_match:
        rec['reassessment_timeline'] = reassessment_match.group(1).strip()
    
    # Extract target strategy
    target_strategy_match = re.search(r'TARGET STRATEGY:(.*?)(?=REASONING:|$)', text, re.DOTALL)
    if target_strategy_match:
        rec['target_strategy'] = target_strategy_match.group(1).strip()
    
    # Extract reasoning
    reasoning_match = re.search(r'REASONING:(.*?)(?=TECHNICAL SIGNALS:|$)', text, re.DOTALL)
    if reasoning_match:
        rec['reasoning'] = reasoning_match.group(1).strip()
    
    # Extract technical signals
    signals_section = re.search(r'TECHNICAL SIGNALS:(.*?)$', text, re.DOTALL)
    if signals_section:
        signals_text = signals_section.group(1)
        for line in signals_text.split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                key = parts[0].strip('- ').strip()
                value = parts[1].strip()
                rec['technical_signals'][key] = value
    
    return rec

