import socket
import requests
from smtplib import SMTP, SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ._config import ConfigError


class Notifier(object):
    def notify(self, title, message):
        raise NotImplementedError()


class NotifierGroup(object):
    def __init__(self):
        self._notifiers = []

    def add_notifier(self, notifier):
        self._notifiers.append(notifier)

    def notify(self, title, message):
        for notifier in self._notifiers:
            notifier.notify(title, message)


class PushbulletNotifier(Notifier):
    PUSH_URL = "https://api.pushbullet.com/v2/pushes"

    def __init__(self, key, prepend_hostname=True):
        self._session = requests.Session()
        self._session.auth = (key, "")
        self._session.headers.update({'Content-Type': 'application/json'})
        self._prepend_hostname = prepend_hostname

    def _prepare_data(self, title, message):
        if self._prepend_hostname:
            title = "{} - {}".format(socket.gethostname(), title)

        return {"type": "note", "title": title, "body": message}

    def notify(self, title, message):
        r = self._session.post(PushbulletNotifier.PUSH_URL, json=self._prepare_data(title, message))
        r.raise_for_status()


class SMTPNotifier(Notifier):
    def __init__(self, host, from_addr, to_addrs, port=0, tls=True, username=None, password=None):
        self._host = host
        self._from_addr = from_addr
        self._to_addrs = to_addrs
        self._port = port
        self._tls = tls
        self._username = username
        self._password = password

    def _prepare_conn(self):
        if self._tls:
            mailserver = SMTP_SSL(self._host, self._port)
        else:
            mailserver = SMTP(self._host, self._port)
        if self._username:
            mailserver.login(self._username, self._password)
        return mailserver

    def _prepare_msg(self, subject, body):
        msg = MIMEMultipart()
        msg["From"] = self._from_addr
        msg["To"] = ", ".join(self._to_addrs)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        return msg

    def notify(self, title, message):
        with self._prepare_conn() as mailserver:
            mailserver.sendmail(self._from_addr, self._to_addrs, self._prepare_msg(title, message).as_string())


def create_notifiers(notifier_config):
    notifier_group = NotifierGroup()
    for n in notifier_config:
        if "type" not in n:
            raise ConfigError("Missing notifer type")
        if n["type"] == "pushbullet":
            notifier_group.add_notifier(PushbulletNotifier(**n["config"]))
        elif n["type"] == "smtp":
            notifier_group.add_notifier(SMTPNotifier(**n["config"]))
        else:
            raise ConfigError("Unknown notifer type {}".format(n['type']))

    return notifier_group
