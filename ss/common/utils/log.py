import datetime
import logging


class CustomFormatter(logging.Formatter):

    def format(self, record):
        if record.levelname == 'WARNING':
            record.levelname = 'WARN'
        return super().format(record)

    def formatTime(self, record, datefmt=None):
        dt = datetime.datetime.fromtimestamp(record.created)
        return dt.isoformat()


class NoStaticFilter(logging.Filter):

    def filter(self, record):
        if 'GET /static' in record.args[0]:
            return False
        return True
