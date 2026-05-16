"""Logging configuration helpers.

Author: Chamath Dilshan
"""

import logging


def configure_logging() -> None:
    """Configure global logging format for API diagnostics."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
