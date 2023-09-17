from random import shuffle
from typing import Any, Callable, Hashable, List, Tuple, Sequence

import numpy as np
from scipy.stats import geom, uniform

Intervals = List[float]
Responses = List[int]


def _eqdiv(n: int) -> List[float]:
    return [(i + 1) / (n + 1) for i in range(n)]


def geom_rng(mean: float, n: int, _shuffle: bool = True) -> Responses:
    resps = geom.ppf(_eqdiv(n), p=1 / mean)
    if mean == 1:
        resps += 1
    if _shuffle:
        shuffle(resps)
    return list(map(lambda x: int(x), resps))


def unif_rng(mean: float,
             _range: float,
             n: int,
             _shuffle: bool = True) -> Intervals:
    if mean < _range:
        raise ValueError("`_range` must be greater than `mean`")
    if not n > 0:
        raise ValueError("`trial` must be greater than 0")
    _min = mean - _range
    l = mean + _range - _min
    intervals = uniform.ppf(_eqdiv(n), _min, l)
    if _shuffle:
        shuffle(intervals)
    return intervals


def expon_rng(mean: float,
              n: int,
              _min: float = 0.,
              _shuffle: bool = True) -> Intervals:
    mean -= _min
    rate = 1 / mean
    intervals: Intervals = []
    for i in range(n - 1):
        i += 1
        s = ((-np.log(1 - rate))**-1) * (1 + np.log(n) +
                                         (n - i) * np.log(n - i) -
                                         (n - i + 1) * np.log(n - i + 1))
        intervals.append(s + _min)
    s = ((-np.log(1 - rate))**-1) * (1 + np.log(n) -
                                     (n - n + 1) * np.log(n - n + 1))
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


class TrialIterator2(object):
    def __init__(self, l: Sequence[Any], *args: Sequence[Any]):
        ls = (l, *args)
        lnc = len(ls)
        lnr = len(l)
        self.__tuples: list[tuple[Any]] = list(map(lambda i: tuple(map(lambda j: ls[j][i], range(lnc))), range(lnr)))
        self.__n = lnr
        self.__idx = range(self.__n)
        self.__now = 0

    def __iter__(self):
        return self

    def __next__(self) -> tuple[int, Any]:
        if self.__now >= self.__n:
            raise StopIteration()
        vals = self.__now, *self.__tuples[self.__now]
        self.__now += 1
        return vals
