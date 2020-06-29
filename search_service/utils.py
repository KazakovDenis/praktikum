from functools import wraps
from os.path import join

from common import get_logger, LOG_DIR


logger = get_logger('uncaught', join(LOG_DIR, 'critical.log'))


def catch(view):
    """Writes to log all uncaught exceptions"""

    @wraps(view)
    def wrapper(*args, **kwargs):

        response = None
        try:
            response = view(*args, **kwargs)
        except Exception as e:
            logger.debug(e.args)
            response = 'Internal server error', 500
        finally:
            return response

    return wrapper
