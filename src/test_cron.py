from loguru import logger
import consts
from pathlib import Path

if __name__ == "__main__":
    logger.add(consts.LOG_FILE + "{time:YYYY-MM-DD}.log", format="{time} {level} {message}", 
                level="INFO")
    logger.info(f"=====Script {Path(__file__).name} launched=====")