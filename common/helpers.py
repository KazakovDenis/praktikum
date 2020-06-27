from typing import Any


__all__ = 'check_type',


def check_type(var: Any, target: type, default: Any = None) -> Any:
    """Check that type of variable is appropriate
    :param var: variable to check
    :param target: type that should be
    :param default: default variable value
    :returns target type instance
    """
    if isinstance(var, target):
        return var
    elif default:
        return default
    else:
        return target()
