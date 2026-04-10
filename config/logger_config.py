import logging
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "app.log"

# logging.basicConfig(
#     level=logging.INFO,
#     format=LOG_FORMAT,
#     handlers=[
#         logging.StreamHandler(),
#         RotatingFileHandler(
#             LOG_FILE,
#             maxBytes=10 * 1024 * 1024,  # 10 MB
#             backupCount=5,
#         ),
#     ]
# )
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
    ]
)



def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)