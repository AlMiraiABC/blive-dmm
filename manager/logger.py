from al_utils.logger import Logger as Lg

from manager.config import Config


class Logger:
    def __init__(self, name: str, log_config: str = "") -> None:
        log_config = log_config or Config().get_app()["log"]["config"]
        if log_config:
            logger = Lg(name, log_config)
        else:
            logger = Lg(name)
        self.logger = logger.logger
