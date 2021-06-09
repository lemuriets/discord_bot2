import logging


file_log = logging.FileHandler('logg/logs.log', encoding='utf-8')
console_out = logging.StreamHandler()

logging.basicConfig(level='INFO',
                    handlers=(file_log, console_out),
                    format='[%(asctime)s] [%(levelname)s] => %(message)s', 
                    datefmt='%d-%m-%Y %H:%M'
                    )

logger = logging.getLogger('python_bot')
logger.setLevel(20)

logging.getLogger('discord').setLevel('CRITICAL')
logging.getLogger('discord_slash').setLevel('CRITICAL')
