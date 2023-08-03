import logging
import sys

__all__ = ['logger']


class ColorFormatter(logging.Formatter):

    def __init__(self,
                 # fmt='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
                 fmt='%(levelname)-8s %(pathname)s:%(lineno)d %(message)s', 
                 datefmt='%H:%M:%S', reset='\x1b[0m',
                ):
        logging.Formatter.__init__(self, fmt=fmt, datefmt=datefmt)
        self.reset = reset

    def format(self, record):
        message = logging.Formatter.format(self, record)

        try:
            color = logging._levelColors[record.levelno]
            message = color + message + self.reset
        except:
            pass

        return message


class ColorStreamHandler(logging.StreamHandler):

    def __init__(self, level=logging.DEBUG, stream=sys.stderr, formatter=ColorFormatter()):
        logging.StreamHandler.__init__(self, stream=stream)

        if formatter is not None:
            self.setFormatter(formatter)


class ColorLogger(logging.Logger):

    def __init__(self, name, level=logging.DEBUG, propagate=False, handlers=[ColorStreamHandler()],
                 colormap={50: '\x1b[1;31m', 40: '\x1b[31m', 30: '\x1b[33m', 20: '\x1b[32m', 10: '\x1b[35m'}):
        try:
            colors = logging._levelColors
        except:
            colors = logging._levelColors = colormap

        logging.Logger.__init__(self, name, level=level)
        self.propagate = propagate

        for handler in handlers:
            self.addHandler(handler)

    @staticmethod
    def _getLevelNumbers():
        return [ik for ik in logging._levelToName.keys() if type(ik) is int]

    @staticmethod
    def _getLevelNames():
        return [sk for sk in logging._levelNames.keys() if type(sk) is str]

    @staticmethod
    def addLevel(levelno, name, color):
        logging._levelNames[levelno] = name
        logging._levelColors[levelno] = color

    @staticmethod
    def testmsgs(logger=None, msg='test message'):
        for level in ColorLogger._getLevelNumbers():
            if logger is None:
                logging.log(level=level, msg=msg)
            else:
                logger.log(level=level, msg=msg)


logger = ColorLogger('colorlogger')

if __name__ == '__main__':
    rootlogger = logging.getLogger()
    logging.basicConfig()

    colorlogger = ColorLogger('colorlogger')

    ColorLogger.testmsgs(rootlogger)
    ColorLogger.testmsgs(colorlogger)
