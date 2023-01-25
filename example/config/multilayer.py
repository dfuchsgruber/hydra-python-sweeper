# example entrypoint for the plugin

from typing import Iterable, Tuple, Any
import itertools

def configure() -> Iterable[Tuple[str, Any]]:
    """This method computes all initializations of arguments to sweep over.

    Returns:
        List[Tuple[str, str]]: A sequence of lists of key, value pairs
    """
    sweep = []
    for num_layers in range(1, 4):
        for num_hidden in itertools.product((32, 64), repeat=num_layers):
            sweep.append({
                'num_layers' : num_layers,
                'num_hidden' : list(num_hidden),
            }.items())
    return sweep