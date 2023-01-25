# example entrypoint for the plugin

from typing import Iterable, Tuple, Any, List
import itertools


def configure() -> Iterable[Iterable[Tuple[str, Any]]]:
    """This method computes all initializations of arguments to sweep over.

    Returns:
        Iterable[Iterable[Tuple[str, str]]]: A sequence of sequences of key, value pairs
    """
    sweep = []
    for num_layers in range(1, 4):
        for num_hidden in itertools.product((32, 64), repeat=num_layers):
            sweep.append({
                'num_layers' : num_layers,
                'num_hidden' : list(num_hidden),
            }.items())
    return sweep

def configure_batch_norm() -> Iterable[Iterable[Tuple[str, Any]]]:
    return [
        (('+batch_norm', True),),
        (('+batch_norm', False),)
    ]

def configure_with_subconfig() -> Iterable[Tuple[str, Any]]:
    from .subconfig import subconfig
    from hydra_plugins.python_sweeper_plugin.utils import merge_overrides
    return merge_overrides(
        configure(),
        subconfig.configure(),
    )
    
    
    