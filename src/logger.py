import logging
import os

os.makedirs("./logs",exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='./logs/app.log',
    filemode='a'
)
