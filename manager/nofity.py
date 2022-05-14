import smtplib
from copy import deepcopy
from email.message import EmailMessage
from email.utils import formataddr

from al_utils.singleton import Singleton
from app_config import NotifyConfig
from utils.config_util import ConfigUtil

from manager.config import ConfigNotify
from manager.logger import Logger

logger = Logger(__file__).logger


class Notify(Singleton):
    def __init__(self, notify: ConfigNotify = None) -> None:
        self.config = self.pre(notify)

    def pre(self, config: ConfigNotify) -> ConfigNotify:
        """
        Pretreatment notfiy config to fill default values.

        :returns: Processed config if exists. Otherwise an empty dict.
        """
        ConfigUtil(config, NotifyConfig.schema_file,
                   valid=NotifyConfig.required)
        c = deepcopy(config)
        sender = c['sender']
        if not sender.get('nickname'):
            sender['nickname'] = ''
            logger.info(f'notify.sender.nickname set to ""')
        receiver = c.get('receiver')
        # default receiver = sender
        if not receiver:
            receiver = [sender]
            c['receiver'] = receiver
            logger.info(f'notify.receiver set to notify.sender {receiver}')
        for rec in receiver:
            if not rec.get('nickname'):
                rec['nickname'] = ''
                logger.info(f'notify.receiver set nickname to ""')
        server = c['server']
        # default server.username = sender.email
        if not server.get('username'):
            username = c['sender']['email']
            server['username'] = username
            logger.info(
                f'notify.server.username set to notify.sender.email {username}')
        # default server.ssl = True
        if not server.get('ssl'):
            server['ssl'] = True
            logger.info(f'notify.server.ssl set to {True}')
        # default server.port = {ssl? 465: 25}
        if not server.get('port'):
            port = 465 if server.get('ssl', True) else 25
            server['port'] = port
            logger.info(f'notify.server.port set to {port}')
        return c

    def send(self, title: str, message: str) -> tuple[bool, Exception | None]:
        """
        Send a email to configured receivers.

        :param title: The header title
        :param message: The Content body.
        :raise ValueError: If not configured.
        :returns:
            1. execute result
            2. exception if falied.
        """
        if not self.config:
            raise ValueError('Email not configured.')
        try:
            sender = self.config['sender']
            receiver = self.config['receiver']
            msg = EmailMessage()
            msg['From'] = formataddr((sender['nickname'], sender['email']))
            msg['To'] = [formataddr((r['nickname'], r['email']))
                         for r in receiver]
            msg['Subject'] = title
            msg.set_content(message)
            server = self.config['server']
            if server['ssl']:
                smtp = smtplib.SMTP_SSL(server['host'], server['port'])
            else:
                smtp = smtplib.SMTP(server['host'], server['port'])
            smtp.login(server['username'], server['passcode'])
            smtp.send_message(msg)
            smtp.quit()
            return (True, None)
        except Exception as ex:
            return(False, ex)
