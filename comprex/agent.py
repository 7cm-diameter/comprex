from typing import List

from amas.agent import OBSERVER as _OBSERVER
from amas.agent import Agent, NotWorkingError
from amas.agent import Observer as _Observer
from pino.ino import HIGH, LOW, Arduino

from comprex.utils import EventTime, timestamp

# Pre-defined messages
START = 0
NEND = 1
ABEND = -1

# Pre-defined agent addresses
OBSERVER = _OBSERVER
STIMULATOR = "stimulator"
READER = "reader"
RECORDER = "recorder"


async def _observe(agent: _Observer) -> None:
    while agent.working():
        _, mess = await agent.recv()
        if mess in (NEND, ABEND):
            agent.send_all(mess)
            agent.finish()
            break
    return None


async def _self_terminate(agent: Agent) -> None:
    try:
        while agent.working():
            _, mess = await agent.recv_from_observer()
            if mess in (NEND, ABEND):
                agent.finish()
                break
    except NotWorkingError:
        pass
    return None


async def _read(agent: Agent, ino: Arduino) -> None:
    try:
        while agent.working():
            v = await agent.call_async(ino.read_until_eol)
            if v is None:
                continue
            s = v.rstrip().decode("utf-8")
            agent.send_to(RECORDER, timestamp(s))
    except NotWorkingError:
        ino.cancel_read()
        pass
    return None


async def _record(agent: Agent, filename: str) -> None:
    """
    Restore receved data and write it to `csv`.
    """
    events: List[EventTime] = []
    try:
        while agent.working():
            _, mess = await agent.recv()
            print(mess)
            events.append(mess)
    except NotWorkingError or KeyboardInterrupt:
        pass
    with open(filename, "w") as f:
        f.write("time, event\n")
        for pack in events:
            t, e = pack
            f.write(f"{t}, {e}\n")
    return None


class Observer(_Observer):
    def __init__(self):
        super().__init__()
        self.assign_task(_observe)


class Reader(Agent):
    def __init__(self, ino: Arduino):
        super().__init__(READER)
        self.assign_task(_read, ino=ino).assign_task(_self_terminate)


class Recorder(Agent):
    def __init__(self, filename: str):
        super().__init__(RECORDER)
        self.assign_task(_record, filename=filename) \
            .assign_task(_self_terminate)


class Stimulator(Agent):
    def __init__(self, ino: Arduino):
        super().__init__(STIMULATOR)
        self.ino = ino

    async def high_for(self, pin: int, duration: float) -> None:
        """
        Set `pin` high for `duration` seconds.
        """
        self.ino.digital_write(pin, HIGH)
        await self.sleep(duration)
        self.ino.digital_write(pin, LOW)
        return None
