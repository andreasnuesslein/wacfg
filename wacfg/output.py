#!/usr/bin/env python

# http://stackoverflow.com/questions/384076/how-can-i-make-the-python-logging-output-to-be-colored

import logging

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

#FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
#FORMAT = "%(levelname)s %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
FORMAT = "%(levelname)s %(message)s"


COLORS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': BLUE,
    'CRITICAL': MAGENTA,
    'ERROR': RED
}

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg = None, use_color = True):
        if not msg:
            msg = FORMAT.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + "*" + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)



OUT = logging.getLogger("mylogger")
OUT.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = ColoredFormatter()
ch.setFormatter(formatter)
OUT.addHandler(ch)

