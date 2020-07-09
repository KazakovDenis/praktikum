from functools import wraps
from os.path import join

from common import get_logger, LOG_DIR
from .app import app


logger = get_logger('uncaught', join(LOG_DIR, 'critical.log'))


def catch(view):
    """Writes to log all uncaught exceptions"""

    @wraps(view)
    def wrapper(*args, **kwargs):

        if app.config.get('DEBUG'):
            return view(*args, **kwargs)

        response = None
        try:
            response = view(*args, **kwargs)
        except Exception as e:
            logger.critical(e.args)
            response = 'Internal server error', 500
        finally:
            return response

    return wrapper
