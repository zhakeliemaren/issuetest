import re
import os
import sys
import logging
from logging import handlers


class LogRecord(logging.LogRecord):

    def __init__(self, name, level, pathname, lineno, msg, args, exc_info, func, sinfo):
        super().__init__(name, level, pathname, lineno, msg, args, exc_info, func, sinfo)
        try:
            self.package = os.path.split(os.path.dirname(pathname))[1]
        except (TypeError, ValueError, AttributeError):
            self.package = "Unknown package"


class StreamHandler(logging.StreamHandler):

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            if stream != sys.stderr:
                print (msg)
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)


class TimedRotatingFileHandler(handlers.TimedRotatingFileHandler):

    def emit(self, record: logging.LogRecord):
        try:
            if self.shouldRollover(record):
                self.doRollover()
            if self.stream is None:
                self.stream = self._open()
            StreamHandler.emit(self, record)
        except Exception:
            self.handleError(record)


class Formatter(logging.Formatter):

    def __init__(
        self,
        show_asctime: bool = True,
        show_level: bool = True,
        show_logger_name: bool = True,
        show_path: bool = False,
        show_file_name: bool = True,
        show_line_no: bool = True,
        show_func_name: bool = True,
        datefmt: str = "%Y-%m-%d %H:%M:%S.%03f"
    ):
        match = re.match('.*([^a-zA-Z]*%(\d*)f)$', datefmt)
        if match:
            groups = match.groups()
            datefmt = datefmt[:-len(groups[0])]
            time_str = '[%(asctime)s%(msecs)' + groups[1] + 'd] '
        else:
            time_str = '[%(asctime)s] '

        fmt = '%(message)s'
        if show_path:
            trace_info = '%(pathname)s'
        elif show_file_name:
            trace_info = '%(package)s/%(filename)s'
        else:
            trace_info = ''
        if trace_info:
            if show_line_no:
                trace_info += ':%(lineno)d'
            fmt = '(%s) %s' % (trace_info, fmt)
        if show_func_name:
            fmt = '%(funcName)s ' + fmt
        if show_logger_name:
            fmt = '[%(name)s] ' + fmt
        if show_level:
            fmt = '%(levelname)s ' + fmt
        if show_asctime:
            fmt = time_str + fmt
            
        super().__init__(fmt, datefmt, style='%', validate=True)


DEFAULT_HANDLER = StreamHandler(None)
DEFAULT_FORMATTER = Formatter()
DEFAULT_LEVEL = 'WARN'
DEFAULT_PATH = None
DEFAULT_INTERVAL = 1
DEFAULT_BACKUP_COUNT = 7


class OBLogger(logging.Logger):

    def __init__(self, name: str, level: str = DEFAULT_LEVEL, path: str = DEFAULT_PATH, interval: int = DEFAULT_INTERVAL, backup_count: int = DEFAULT_BACKUP_COUNT, formatter: Formatter = DEFAULT_FORMATTER):
        super().__init__(name, level)
        self.handlers = []
        self._interval = interval
        self._backup_count = backup_count
        self._formatter = formatter
        self._path = self._format_path(path) if path else None
        self._default_handler = None
        self._create_file_handler()

    @property
    def interval(self):
        return self._interval
        
    @property
    def backup_count(self):
        return self._backup_count

    @property
    def formatter(self):
        return self._formatter

    @property
    def path(self):
        return self._path

    @interval.setter
    def interval(self, interval: int):
        if interval != self._interval:
            self._interval = interval
            self._create_file_handler()

    @backup_count.setter
    def backup_count(self, backup_count: int):
        if backup_count != self._backup_count:
            self._backup_count = backup_count
            self._create_file_handler()

    @formatter.setter
    def formatter(self, formatter: Formatter):
        if formatter != self._formatter:
            self._formatter = formatter
            self._create_file_handler()

    @path.setter
    def path(self, path):
        path = self._format_path(path) if path else None
        if path and path != self._path:
            self._path = path
            self._create_file_handler()

    def _create_file_handler(self):
        if self._default_handler:
            self.removeHandler(self._default_handler)
        if self.path:
            self._default_handler = TimedRotatingFileHandler(self.path, when='midnight', interval=self.interval, backupCount=self.backup_count)
        else:
            self._default_handler = DEFAULT_HANDLER
        self._default_handler.setFormatter(self.formatter)
        self.addHandler(self._default_handler)

    def _format_path(self, path: str):
        return path % self.__dict__


class LoggerFactory(object):

    LOGGERS = logging.Logger.manager.loggerDict
    GLOBAL_CONFIG = {}

    @classmethod
    def init(cls):
        if logging.getLoggerClass() != OBLogger:
            logging.setLoggerClass(OBLogger)
            logging.setLogRecordFactory(LogRecord)
            # logging.basicConfig()
            cls.update_global_config()
         
    @classmethod
    def update_global_config(cls, level: str = DEFAULT_LEVEL, path: str = DEFAULT_PATH, interval: int = DEFAULT_INTERVAL, backup_count: int = DEFAULT_BACKUP_COUNT, formatter: Formatter = DEFAULT_FORMATTER):
        args = locals()
        updates = {}
        for key in args:
            value = args[key]
            if value != cls.GLOBAL_CONFIG.get(key):
                cls.GLOBAL_CONFIG[key] = updates[key] = value
        update_path = updates.get(path)
                
        if updates:
            for name in cls.LOGGERS:
                logger = cls.LOGGERS[name]
                if not isinstance(logger, logging.Logger):
                    continue
                for key in updates:
                    if key == 'level':
                        logger.setLevel(updates[key])
                    else:
                        setattr(logger, key, updates[key])
                if update_path and not isinstance(logger, OBLogger):
                    logger.handlers = [logger.handlers.append(TimedRotatingFileHandler(path, when='midnight', interval=interval, backupCount=backup_count))]

    @classmethod
    def create_logger(cls, name: str, level: str = DEFAULT_LEVEL, path: str = DEFAULT_PATH, interval: int = DEFAULT_INTERVAL, backup_count: int = DEFAULT_BACKUP_COUNT, formatter: Formatter = DEFAULT_FORMATTER):
        if name in cls.LOGGERS:
            raise Exception('Logger `%s` has been created' % name)
        args = locals()
        logging._acquireLock()
        logger = logging.getLogger(name)
        cls.LOGGERS[name] = logger
        logging._releaseLock()
        return logger

    @classmethod
    def get_logger(cls, name: str):
        logger = cls.LOGGERS.get(name)
        if logger is None:
            logger = cls.create_logger(name)
        return logger


LoggerFactory.init()