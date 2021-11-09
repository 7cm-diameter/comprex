from datetime import datetime
from os.path import abspath, dirname
from time import perf_counter
from typing import Any, Optional, Tuple

from comprex.config import Metadata

Event = Any
Time = float
EventTime = Tuple[Time, Event]


def timestamp(event: Event) -> EventTime:
    """
    Return the tuple of current time and a given event.
    """
    return perf_counter(), event


def namefile(meta: Metadata,
             timeformat: Optional[str] = "%y%m%d%H%M",
             tfseparator: Optional[str] = "-",
             separator: str = "_",
             extension: str = "csv") -> str:
    now = ""
    if timeformat is not None:
        if tfseparator is not None:
            components = list(filter(lambda c: c != "", timeformat.split("%")))
            timeformat = "%" + (tfseparator + "%").join(components)
        now = datetime.now().strftime(timeformat)
    experiment = meta.get("experiment", "")
    sub = meta.get("subject", "")
    cond = meta.get("condition", "")
    components = [experiment, sub, cond, now]
    try:
        components = list(filter(lambda c: c != "", components))
    except ValueError:
        pass
    stem = separator.join(components)
    if extension.startswith("."):
        return stem + extension
    return stem + "." + extension


def get_current_file_abspath(relpath: str) -> str:
    return dirname(abspath(relpath))
