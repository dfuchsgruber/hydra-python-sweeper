# example subconfiguration

from typing import Iterable, Tuple, Any

def configure() -> Iterable[Tuple[str, Any]]:
    """This method computes all initializations of arguments to sweep over.

    Returns:
        List[Tuple[str, str]]: A sequence of lists of key, value pairs
    """
    sweep = []
    for dropout in (0.1, 0.5):
        sweep.append({
            '+dropout' : dropout,
        }.items())
    return sweep