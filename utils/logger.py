import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricsLogger:
    def __init__(self):
        self.cache = {}

    def get_cache(self, query: str):
        return self.cache.get(query)

    def set_cache(self, query: str, response: dict):
        self.cache[query] = response

    def log_event(self, event: dict):
        """
        Logs an observatory event.
        Expected keys in event: query, latency, tokens, agent, cost
        """
        log_info = {
            "query": event.get("query", ""),
            "latency": event.get("latency", 0.0),
            "tokens": event.get("tokens", 0),
            "agent": event.get("agent", "unknown"),
            "cost": event.get("cost", 0.0)
        }
        logger.info(f"LangGraph Event Trace: {log_info}")
        return log_info

metrics_logger = MetricsLogger()
