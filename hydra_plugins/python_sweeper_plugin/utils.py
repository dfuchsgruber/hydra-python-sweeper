from typing import Iterable, Tuple, Any, List
import itertools

def merge_overrides(*overrides: Iterable[Iterable[Iterable[Tuple[str, Any]]]]) -> Iterable[Iterable[Tuple[str, Any]]]:
    """ Merges any number of overrides building a cartesian product between them.

    Args:
        overrides: Iterable[Iterable[Iterable[Tuple[str, Any]]]]: An iterable of overrides to merge.

    Returns:
        Iterable[Iterable[Tuple[str, Any]]]: The merged overrides
    """
    return [sum(map(tuple, configs), start=()) for configs in itertools.product(*overrides)]

def compress_override(overrides: Iterable[Tuple[str, Any]]) -> Tuple[Tuple[str, Any]]:
    """Compresses an override sequence such that it contains no duplicate keys.

    Args:
        overrides (Iterable[Tuple[str, Any]]): the seqence to compress

    Returns:
        Tuple[Tuple[str, Any]]: the compressed sequence
    """
    result = []
    result_keys = set()
    for key, value in overrides:
        if key.lstrip('+') not in result_keys:
            result.append((key, value))
            result_keys.add(key.lstrip('+'))
    return tuple(result)
    
    
    
