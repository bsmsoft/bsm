import time
import logging

_MAIN_LOGGER_NAME = 'CEPCENV'

def _time_zone(t):
    if t.tm_isdst == 1 and time.daylight == 1:
        tz_sec = time.altzone
        tz_name = time.tzname[1]
    else:
        tz_sec = time.timezone
        tz_name = time.tzname[0]

    if tz_sec > 0:
        tz_sign = '-'
    else:
        tz_sign = '+'

    tz_offset = '%s%02d%02d' % (tz_sign, abs(tz_sec)//3600, abs(tz_sec//60)%60)
    return (tz_offset, tz_name)


class JsubFormatter(logging.Formatter):
    # Add this method in order to display time zone offset correctly under python 2.x
    def formatTime(self, record, datefmt=None):
        ct = time.localtime(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime('%Y-%m-%d %H:%M:%S', ct)

            ms = '%03d' % record.msecs

            tz_offset, tz_name = _time_zone(ct)
            s = '%s.%03d %s %s' % (t, record.msecs, tz_offset, tz_name)
        return s


_FORMATTER = JsubFormatter('[%(asctime)s][%(name)s|%(levelname)s] %(message)s')
#_FORMATTER = logging.Formatter('[%(asctime)s](%(name)s:%(levelname)s) %(message)s', '%Y-%m-%d %H:%M:%S')

_FORMATTER_SIMPLE = logging.Formatter('[%(levelname)s] %(message)s')


def add_stream_logger(verbose=False):
    logger = logging.getLogger(_MAIN_LOGGER_NAME)

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    if verbose:
        ch.setFormatter(_FORMATTER)
    else:
        ch.setFormatter(_FORMATTER_SIMPLE)

    logger.addHandler(ch)

def get_logger():
    return logging.getLogger(_MAIN_LOGGER_NAME)
