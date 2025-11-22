from typing import Annotated, Dict

from langchain_core.messages import HumanMessage, RemoveMessage
from langchain_core.tools import tool

from cointradingagents.dataflows import interface
from cointradingagents.default_config import DEFAULT_CONFIG


def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility."""
        messages = state["messages"]
        removal_operations = [RemoveMessage(id=m.id) for m in messages]
        placeholder = HumanMessage(content="Continue")
        return {"messages": removal_operations + [placeholder]}

    return delete_messages


class Toolkit:
    _config: Dict = DEFAULT_CONFIG.copy()

    @classmethod
    def update_config(cls, config: Dict):
        cls._config.update(config)

    @property
    def config(self):
        return self._config

    def __init__(self, config=None):
        if config:
            self.update_config(config)

    @staticmethod
    def _unsupported(feature: str) -> str:
        return f"{feature} data source is not available in the CoinTradingAgents pipeline."

    @staticmethod
    @tool
    def get_reddit_news(
        curr_date: Annotated[str, "Date you want to get news for in yyyy-mm-dd format"],
    ) -> str:
        return Toolkit._unsupported("Reddit global news")

    @staticmethod
    @tool
    def get_finnhub_news(
        ticker: Annotated[str, "Search query of an asset"],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ) -> str:
        return Toolkit._unsupported("Finnhub news")

    @staticmethod
    @tool
    def get_reddit_stock_info(
        ticker: Annotated[str, "Asset or project name"],
        curr_date: Annotated[str, "Current date you want to get news for"],
    ) -> str:
        return Toolkit._unsupported("Reddit asset-specific news")

    @staticmethod
    @tool
    def get_YFin_data(
        symbol: Annotated[str, "Coin pair symbol, e.g., BTCUSDT"],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ) -> str:
        return interface.get_binance_price_data(symbol, start_date, end_date)

    @staticmethod
    @tool
    def get_YFin_data_online(
        symbol: Annotated[str, "Coin pair symbol, e.g., BTCUSDT"],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ) -> str:
        return interface.get_binance_price_data(symbol, start_date, end_date)

    @staticmethod
    @tool
    def get_stockstats_indicators_report(
        symbol: Annotated[str, "Coin pair symbol, e.g., BTCUSDT"],
        indicator: Annotated[str, "Indicator name. Must be one of: ['close_50_sma', 'close_200_sma', 'close_10_ema', 'macd', 'macds', 'macdh', 'rsi', 'boll', 'boll_ub', 'boll_lb', 'atr', 'vwma']"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
        look_back_days: Annotated[int, "how many days to look back"] = 30,
    ) -> str:
        # Validate indicator before calling
        if not indicator or not indicator.strip():
            return f"Error: Indicator parameter is required and cannot be empty. Please provide one of: ['close_50_sma', 'close_200_sma', 'close_10_ema', 'macd', 'macds', 'macdh', 'rsi', 'boll', 'boll_ub', 'boll_lb', 'atr', 'vwma']"
        return interface.get_binance_indicator_report(symbol, indicator, curr_date, look_back_days)

    @staticmethod
    @tool
    def get_stockstats_indicators_report_online(
        symbol: Annotated[str, "Coin pair symbol, e.g., BTCUSDT"],
        indicator: Annotated[str, "Indicator name. Must be one of: ['close_50_sma', 'close_200_sma', 'close_10_ema', 'macd', 'macds', 'macdh', 'rsi', 'boll', 'boll_ub', 'boll_lb', 'atr', 'vwma']"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
        look_back_days: Annotated[int, "how many days to look back"] = 30,
    ) -> str:
        # Validate indicator before calling
        if not indicator or not indicator.strip():
            return f"Error: Indicator parameter is required and cannot be empty. Please provide one of: ['close_50_sma', 'close_200_sma', 'close_10_ema', 'macd', 'macds', 'macdh', 'rsi', 'boll', 'boll_ub', 'boll_lb', 'atr', 'vwma']"
        return interface.get_binance_indicator_report(symbol, indicator, curr_date, look_back_days)

    @staticmethod
    @tool
    def get_finnhub_company_insider_sentiment(
        ticker: Annotated[str, "Asset identifier"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ) -> str:
        return Toolkit._unsupported("Insider sentiment")

    @staticmethod
    @tool
    def get_finnhub_company_insider_transactions(
        ticker: Annotated[str, "Asset identifier"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ) -> str:
        return Toolkit._unsupported("Insider transactions")

    @staticmethod
    @tool
    def get_simfin_balance_sheet(
        ticker: Annotated[str, "Asset identifier"],
        freq: Annotated[str, "frequency"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ) -> str:
        return Toolkit._unsupported("Balance sheet data")

    @staticmethod
    @tool
    def get_simfin_cashflow(
        ticker: Annotated[str, "Asset identifier"],
        freq: Annotated[str, "frequency"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ) -> str:
        return Toolkit._unsupported("Cashflow data")

    @staticmethod
    @tool
    def get_simfin_income_stmt(
        ticker: Annotated[str, "Asset identifier"],
        freq: Annotated[str, "frequency"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ) -> str:
        return Toolkit._unsupported("Income statement data")

    @staticmethod
    @tool
    def get_google_news(
        query: Annotated[str, "Query to search with"],
        curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    ) -> str:
        return interface.get_google_news(query, curr_date, 3)

    @staticmethod
    @tool
    def get_stock_news_openai(
        ticker: Annotated[str, "Asset ticker or name"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ) -> str:
        return interface.get_stock_news_openai(ticker, curr_date)

    @staticmethod
    @tool
    def get_global_news_openai(
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ) -> str:
        return interface.get_global_news_openai(curr_date)

    @staticmethod
    @tool
    def get_fundamentals_openai(
        ticker: Annotated[str, "Asset ticker or name"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ) -> str:
        return interface.get_stock_news_openai(ticker, curr_date)
