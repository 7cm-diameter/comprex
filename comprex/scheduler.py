from random import shuffle
from typing import Any, Callable, Hashable, List, Tuple

from numpy import log

Intervals = List[float]


def uniform_intervals(mean: float,
                      _range: float,
                      n: int,
                      _shuffle: bool = True) -> Intervals:
    if mean < _range:
        raise ValueError("`_range` must be greater than `mean`")
    if not n > 0:
        raise ValueError("`trial` must be greater than 0")
    _min = mean - _range
    d = mean / n
    intervals: Intervals = [_min + step * d for step in range(n)]
    if _shuffle:
        shuffle(intervals)
    return intervals


def exponential_intervals(mean: float,
                          n: int,
                          _min: float = 0.,
                          _shuffle: bool = True) -> Intervals:
    mean -= _min
    rate = 1 / mean
    intervals: Intervals = []
    for i in range(n - 1):
        i += 1
        s = ((-log(1 - rate))**-1) * (1 + log(n) + (n - i) * log(n - i) -
                                      (n - i + 1) * log(n - i + 1))
        intervals.append(s + _min)
    s = ((-log(1 - rate))**-1) * (1 + log(n) - (n - n + 1) * log(n - n + 1))
    intervals.append(s + _min)
    if _shuffle:
        shuffle(intervals)
    return intervals


def elementwise_shuffle(x: List[Any]) -> List[Any]:
    from copy import copy
    _x = copy(x)
    shuffle(_x)
    return _x


def blockwise_shuffle(x: List[Any], blocksize: int) -> List[Any]:
    length = len(x)
    if not length % blocksize == 0:
        raise ValueError("`x` must be dividable by `blocksize`")
    offsets = list(range(0, length + 1, blocksize))
    ret: List[Any] = []
    for i in range(length // blocksize):
        _x = x[offsets[i]:offsets[i + 1]]
        shuffle(_x)
        ret.extend(_x)
    return ret


def repeat(values: List[Any], repeats: List[int]) -> List[Any]:
    if not len(values) == len(repeats):
        raise ValueError("`values` and `repeats` must be the same length.")
    ret: List[Any] = []
    for v, n in zip(values, repeats):
        ret.extend([v for _ in range(n)])
    return ret


class TrialIterator(object):
    def __init__(self, ids: List[Hashable], x: List[Any]):
        if not len(x) == len(ids):
            raise ValueError("`x` and `ids` must be the same length.")
        self.__trialmap = dict(zip(ids, x))
        self.__seq: List[Hashable] = ids
        self.__now = 0

    def __len__(self) -> int:
        return len(self.__seq)

    def __iter__(self):
        return self

    def __next__(self) -> Tuple[Any, ...]:
        if self.__now >= len(self):
            self.__now = 0
            raise StopIteration()
        key = self.__seq[self.__now]
        val = self.__trialmap[key]
        self.__now += 1
        return key, val

    def set_sequence(self, seq: List[Hashable]) -> "TrialIterator":
        self.__seq = seq
        return self

    def shuffle(self, method: Callable[..., List[Any]], *args,
                **kwargs) -> "TrialIterator":
        self.__seq = method(self.__seq, *args, **kwargs)
        return self
