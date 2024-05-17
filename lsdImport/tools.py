#!/bin/env python3
"""Tools module"""

import logging


class LoggerConfig:
    @staticmethod
    def get_logger(name, handler=None):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)  # Nastavení úrovně logování
        if handler:
            logger.addHandler(handler)  # Přidání specifikovaného handleru
        else:
            # Vytvoření handleru pro logování do konzole
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)  #

        return logger
