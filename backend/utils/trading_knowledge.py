"""
Trading Platform Knowledge Base

Common questions and answers about trading platforms (Robinhood-style).
Used as fallback when documents are not available.
"""
from typing import Dict, List

# Knowledge base for common trading questions
TRADING_KNOWLEDGE_BASE = """[TRADING EDUCATION KNOWLEDGE BASE - Educational Information]

NOTE: TradePal is an educational/informational tool, not a trading platform. This knowledge helps users learn about trading, especially patterns in SPY and Tesla (TSLA).

GETTING STARTED WITH TRADING:
Q: How do I get started with trading?
A: Research trading basics, understand SEC/FINRA regulations, learn about different order types, study market patterns (especially SPY and Tesla), and practice with paper trading before using real money.

Q: What should I learn first?
A: Start with: market basics, order types (market/limit/stop), SEC/FINRA rules (PDT, settlement), risk management, and pattern analysis. Focus on understanding SPY and Tesla patterns as they're commonly traded.

Q: What is KYC/AML?
A: SEC/FINRA requirement: Know Your Customer (KYC) and Anti-Money Laundering (AML) verification. All U.S. brokerages must verify identity and monitor for suspicious activity when you open an account.

Q: How do brokerages handle deposits?
A: Most brokerages allow ACH transfer (free, 1-3 business days) or instant deposit with debit card (instant, fee applies). SEC requires broker verification of funding sources.

Q: How do brokerages handle withdrawals?
A: Transfer to linked bank account via ACH (free, 1-3 business days) or wire transfer (fee, same day). SEC requires withdrawal to verified accounts only.

TRADING BASICS & PATTERNS:
Q: What can I trade?
A: Stocks (like SPY, TSLA), ETFs, options, and cryptocurrency. Some assets require account approval (options, margin) per SEC/FINRA regulations. Focus on learning patterns in popular stocks like SPY and Tesla.

Q: What are trading hours?
A: Regular hours: 9:30 AM - 4:00 PM ET (NYSE/NASDAQ). Extended hours: 4:00 AM - 9:30 AM ET and 4:00 PM - 8:00 PM ET. Set by exchanges. SPY and Tesla trade during these hours.

Q: How do I analyze trading patterns?
A: Study price movements, volume, support/resistance levels, and sentiment. SPY (S&P 500 ETF) shows overall market trends. Tesla (TSLA) often shows high volatility patterns. Look for correlations between them.

Q: What is a market order?
A: Executes immediately at current market price. Fastest execution but price may vary slightly. SEC requires best execution. Use for urgent trades.

Q: What is a limit order?
A: Sets maximum price to buy or minimum price to sell. Only executes if price reaches your limit. Protects against price slippage. Better for SPY/Tesla pattern trading.

Q: What is a stop loss order?
A: Automatically sells if price drops to your specified level. Helps limit losses. Becomes market order when triggered. Important for managing risk in volatile stocks like Tesla.

Q: What patterns should I watch in SPY?
A: SPY often shows: pre-market gaps, intraday reversals, correlation with VIX, end-of-day momentum. Study volume patterns and support/resistance levels.

Q: What patterns should I watch in Tesla (TSLA)?
A: Tesla often shows: high volatility, gap-and-go patterns, correlation with tech sector, earnings-related moves, CEO tweet impacts. Volume spikes often precede big moves.

Q: What is a short sale?
A: Borrowing stock to sell, hoping to buy back cheaper. SEC requires: locate requirement (find shares to borrow) and uptick rule for some stocks. Higher risk than buying.

Q: What is after-hours trading?
A: Trading outside 9:30 AM - 4:00 PM ET. Lower liquidity, wider spreads. SEC allows but with disclosure requirements. SPY and Tesla can trade after hours.

DAY TRADING (PDT RULE - SEC/FINRA REGULATION):
Q: What is the Pattern Day Trader (PDT) rule?
A: The PDT rule is a SEC/FINRA regulation (not a TradePal rule). If you make 4+ day trades in 5 business days with account under $25,000, you're marked as PDT and restricted from day trading for 90 days. This applies to all U.S. brokerages.

Q: What counts as a day trade?
A: Buying and selling the same stock on the same trading day.

Q: How do I avoid PDT restrictions?
A: Keep account balance above $25,000 OR limit day trades to 3 or fewer in any 5-day period. This is a federal regulation enforced by FINRA, not a platform-specific rule.

MARGIN TRADING (SEC/FINRA REGULATION):
Q: What is margin?
A: Borrowing money from the broker to buy more securities than your cash allows. Regulated by SEC/FINRA.

Q: What is the minimum for margin?
A: $2,000 minimum account balance required by SEC/FINRA regulation (applies to all U.S. brokerages). Margin interest rates vary (typically 2-8% annually).

Q: What is a margin call?
A: FINRA rule: When account equity falls below maintenance requirement (typically 25-30% of margin value), broker may require additional funds or sell positions. Must meet call within timeframe or positions liquidated.

Q: What is margin maintenance requirement?
A: FINRA rule: Minimum equity percentage (usually 25-30%) that must be maintained in margin account. If equity drops below, margin call issued. Varies by security type.

OPTIONS TRADING (SEC/FINRA REGULATION):
Q: How do I get approved for options?
A: Apply in app settings, answer questions about experience and risk tolerance. SEC/FINRA requires broker assessment. Approval levels: Level 1 (covered calls), Level 2 (long options), Level 3 (spreads), Level 4 (naked options).

Q: What are options?
A: Contracts giving right (not obligation) to buy (call) or sell (put) stock at set price by expiration date. Regulated by SEC/FINRA.

Q: What is options contract fee?
A: $0.65 per contract. Example: 10 contracts = $6.50 fee. Fees set by broker, but SEC requires disclosure.

Q: What is options assignment?
A: When option holder exercises right to buy/sell. SEC rule: Automatic assignment on expiration if in-the-money. Can happen early for American-style options.

Q: What is the Options Clearing Corporation (OCC)?
A: SEC-regulated entity that guarantees all options contracts. Ensures options are honored even if broker fails. Required by federal regulation.

SETTLEMENT & FUNDS (SEC/FINRA REGULATION):
Q: When do trades settle?
A: Stock trades settle T+2 (2 business days after trade) - SEC regulation. Options settle T+1 (next business day). This applies to all U.S. brokerages.

Q: What is settled cash?
A: Cash available to withdraw. Unsettled funds can be used for new trades but not withdrawn until settlement completes.

Q: What is buying power?
A: Total amount you can spend on trades, including margin (if approved). Cash accounts: settled cash only. Margin accounts: settled cash + margin.

Q: What is a Good Faith Violation (GFV)?
A: SEC/FINRA rule: Buying stock with unsettled funds, then selling before funds settle. 3 GFVs in 12 months = 90-day cash account restriction (no buying with unsettled funds).

Q: What is a Free Riding Violation?
A: SEC/FINRA rule: Buying stock without sufficient settled funds, then selling before payment. Results in immediate 90-day cash account restriction.

Q: Can I use unsettled funds to buy and sell?
A: In cash accounts: No - must wait for settlement (T+2) before selling. In margin accounts: Yes, but margin interest applies.

TAXES (IRS/SEC REGULATION):
Q: Do I get tax forms?
A: Yes, 1099 forms sent by January 31st for accounts with $10+ in dividends or $600+ in proceeds. Required by IRS regulation.

Q: What is a wash sale?
A: IRS rule: Selling stock at loss and buying same/similar stock within 30 days. Loss disallowed for tax purposes. Applies to all U.S. taxpayers.

Q: What is cost basis reporting?
A: SEC/IRS regulation: Brokers must report cost basis for covered securities. Helps calculate capital gains/losses for taxes.

Q: When are taxes due on trading profits?
A: Capital gains taxed in year realized. Short-term (held <1 year): ordinary income rates. Long-term (held >1 year): lower capital gains rates.

SECURITY & SAFETY (SEC/FINRA REGULATION):
Q: Is my money safe?
A: Accounts are SIPC insured up to $500,000 (cash up to $250,000) - federal regulation. Securities held in your name, not the broker's.

Q: What is SIPC insurance?
A: SEC-mandated insurance: Protects up to $500,000 per account ($250,000 cash) if broker fails. Covers securities, not trading losses.

Q: What if the app is hacked?
A: Report immediately. Accounts have fraud protection. Enable 2FA for extra security. Brokers required to report suspicious activity to FINRA/SEC.

Q: How do I enable two-factor authentication?
A: Go to Settings > Security > Enable 2FA. Use authenticator app or SMS. Recommended by SEC/FINRA for account security.

Q: What is account segregation?
A: SEC rule: Customer securities must be held separately from broker assets. Protects your holdings if broker goes bankrupt.

COMMON TRADING MISTAKES & EDUCATION:
Q: What are common trading mistakes beginners make?
A: Not using stop losses, overtrading, ignoring SEC/FINRA rules (PDT, GFV), not understanding settlement (T+2), trading on emotion, not studying patterns first. Learn SPY/Tesla patterns before trading.

Q: How do I avoid trading mistakes?
A: Paper trade first, study SPY and Tesla patterns, understand SEC/FINRA regulations, use stop losses, manage position sizes, don't trade on emotions, learn from losses.

Q: Why do orders sometimes not execute?
A: Limit price not reached, outside trading hours, insufficient buying power, account restrictions (PDT, GFV), or market volatility. Study order types and execution rules.

Q: Why can't I withdraw funds immediately?
A: SEC settlement rule (T+2): Funds must settle before withdrawal. Stocks settle 2 business days after trade. Options settle next day. This applies to all brokerages.

Q: How do I learn to read trading patterns?
A: Study SPY and Tesla charts, learn support/resistance, volume analysis, correlation patterns, sentiment indicators. Practice with paper trading. Focus on understanding why moves happen.

TRADING PATTERNS & ANALYSIS:
Q: What patterns should I study in SPY?
A: SPY (S&P 500 ETF) patterns: pre-market gaps, intraday reversals, VIX correlation, end-of-day momentum, volume spikes, support/resistance levels. Often moves with overall market sentiment.

Q: What patterns should I study in Tesla (TSLA)?
A: Tesla patterns: high volatility swings, gap-and-go moves, earnings-related volatility, tech sector correlation, volume spikes before big moves, CEO-related news impacts. Often shows 5-10% daily moves.

Q: How do SPY and Tesla correlate?
A: SPY represents overall market. Tesla often moves with tech sector but can diverge. When SPY drops, Tesla often drops more (higher beta). When SPY rallies, Tesla can outperform. Study their correlation patterns.

Q: What is fractional shares?
A: Buy partial shares (e.g., $10 of a $100 stock = 0.1 shares). Available for most stocks including SPY and Tesla. Helps with position sizing.

Q: What is dividend reinvestment?
A: Automatically uses dividends to buy more shares. SPY pays dividends quarterly. Tesla doesn't pay dividends. Can enable/disable in brokerage settings.

Q: What is recurring investments?
A: Automatically invest set amount on schedule (daily, weekly, monthly). Useful for dollar-cost averaging into SPY or Tesla. Set up in brokerage app.

Q: What is cash management?
A: Interest-earning account for uninvested cash. FDIC insured up to $250,000. Available at most brokerages.

COMMON ERRORS:
Q: "Insufficient buying power"
A: Not enough cash or margin available. Check account balance and pending orders. May also be due to unsettled funds in cash accounts.

Q: "Order rejected"
A: May be outside trading hours, invalid order type, insufficient funds, account restrictions, or SEC/FINRA compliance issues (PDT, GFV, etc.).

Q: "Symbol not found"
A: Stock may be delisted, ticker incorrect, or not available on platform. Some securities restricted by SEC (penny stocks, foreign stocks).

Q: "Account restricted"
A: May be due to: PDT rule violation, Good Faith Violation (GFV), Free Riding Violation, or other SEC/FINRA compliance issues. Check account status.

Q: "Trade rejected - settlement violation"
A: SEC rule: In cash accounts, cannot sell stock bought with unsettled funds until T+2 settlement. Wait for funds to settle or use margin account.

Q: "Margin call"
A: FINRA rule: Account equity below maintenance requirement. Must deposit funds or broker may liquidate positions. Minimum maintenance typically 25-30% of margin value."""


def get_trading_knowledge() -> str:
    """Get the trading knowledge base."""
    return TRADING_KNOWLEDGE_BASE


def search_knowledge_base(query: str) -> str:
    """
    Search knowledge base for relevant information.
    
    Args:
        query: User's question
        
    Returns:
        Relevant knowledge section or empty string
    """
    query_lower = query.lower()
    
    # Simple keyword matching to find relevant sections
    keywords_to_sections = {
        'pricing': 'PRICING PLANS',
        'price': 'PRICING PLANS',
        'plan': 'PRICING PLANS',
        'subscription': 'PRICING PLANS',
        'fee': 'TRADING FEES',
        'commission': 'TRADING FEES',
        'cost': 'TRICING FEES',
        'deposit': 'ACCOUNT BASICS',
        'withdraw': 'ACCOUNT BASICS',
        'transfer': 'ACCOUNT BASICS',
        'account': 'ACCOUNT BASICS',
        'open account': 'ACCOUNT BASICS',
        'kyc': 'ACCOUNT BASICS',
        'aml': 'ACCOUNT BASICS',
        'day trade': 'DAY TRADING',
        'pdt': 'DAY TRADING',
        'pattern day trader': 'DAY TRADING',
        'margin': 'MARGIN TRADING',
        'margin call': 'MARGIN TRADING',
        'maintenance': 'MARGIN TRADING',
        'options': 'OPTIONS TRADING',
        'call': 'OPTIONS TRADING',
        'put': 'OPTIONS TRADING',
        'assignment': 'OPTIONS TRADING',
        'occ': 'OPTIONS TRADING',
        'settle': 'SETTLEMENT',
        'settlement': 'SETTLEMENT',
        'buying power': 'SETTLEMENT',
        't+2': 'SETTLEMENT',
        't+1': 'SETTLEMENT',
        'gfv': 'SETTLEMENT',
        'good faith violation': 'SETTLEMENT',
        'free riding': 'SETTLEMENT',
        'unsettled': 'SETTLEMENT',
        'tax': 'TAXES',
        '1099': 'TAXES',
        'wash sale': 'TAXES',
        'cost basis': 'TAXES',
        'capital gains': 'TAXES',
        'security': 'SECURITY',
        'hack': 'SECURITY',
        '2fa': 'SECURITY',
        'two factor': 'SECURITY',
        'sipc': 'SECURITY',
        'insurance': 'SECURITY',
        'segregation': 'SECURITY',
        'order': 'TROUBLESHOOTING',
        'execute': 'TROUBLESHOOTING',
        'not working': 'TROUBLESHOOTING',
        'error': 'COMMON ERRORS',
        'rejected': 'COMMON ERRORS',
        'insufficient': 'COMMON ERRORS',
        'restricted': 'COMMON ERRORS',
        'violation': 'COMMON ERRORS',
        'trade': 'TRADING BASICS',
        'market order': 'TRADING BASICS',
        'limit order': 'TRADING BASICS',
        'stop loss': 'TRADING BASICS',
        'short sale': 'TRADING BASICS',
        'after hours': 'TRADING BASICS',
        'hours': 'TRADING BASICS',
        'sec': 'DAY TRADING',  # SEC questions often about PDT
        'finra': 'DAY TRADING',  # FINRA questions often about PDT
        'regulation': 'DAY TRADING',  # Regulation questions often about PDT
    }
    
    # Find matching sections
    relevant_sections = []
    for keyword, section in keywords_to_sections.items():
        if keyword in query_lower:
            relevant_sections.append(section)
    
    if not relevant_sections:
        return TRADING_KNOWLEDGE_BASE  # Return all if no specific match
    
    # Extract relevant sections from knowledge base
    sections = TRADING_KNOWLEDGE_BASE.split('\n\n')
    result_parts = []
    
    for section in sections:
        for target_section in relevant_sections:
            if target_section in section:
                result_parts.append(section)
                break
    
    if result_parts:
        return '\n\n'.join(result_parts)
    
    return TRADING_KNOWLEDGE_BASE

