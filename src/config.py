from logging import Formatter, getLogger, INFO, Logger, StreamHandler

from yaml import CDumper, CLoader, dump, load


def init_logger() -> Logger:
    logger = getLogger(__name__)

    console_handler = StreamHandler()
    console_handler.setFormatter(Formatter("%(asctime)s %(levelname)s %(message)s"))

    logger.setLevel(INFO)
    logger.addHandler(console_handler)

    logger.info("Logger initialized successfully.")
    return logger


class Config:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        self.data = {
            "tech": {
                "api_id": 0,
                "api_hash": "0",
                "admin_id": 0
            }
        }

    def load_config(self, config_filename: str) -> None:
        config_file_path = f'./{config_filename}'

        try:
            with open(config_file_path, "r") as config_file:
                config = load(config_file, Loader=CLoader)
                self.data = config
                self.logger.info(f'Config successfully loaded. Data: {self.data}')
        except:
            config_file = open(config_file_path, "w+")
            config_file.write(dump(self.data, Dumper=CDumper))

            self.logger.info('Created new config file.')
            config_file.close()

            raise Exception("Enter the auth keys into config file.")
