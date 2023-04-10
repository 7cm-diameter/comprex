from typing import Optional

from nptyping import Float32, NDArray
from numpy import arange, float32, pi, sin
from numpy.random import uniform
from sounddevice import play, query_devices, stop

Wave = NDArray[Float32]


class Tone(object):
    def __init__(self,
                 wave: Wave,
                 duration: float,
                 amp: float,
                 samplerate: int = 48000):
        self.__wave = wave
        self.__amp = amp
        self.__duration = duration
        self.__samplerate = samplerate

    @property
    def wave(self) -> Wave:
        return self.__wave

    @property
    def duration(self) -> float:
        return self.__duration

    @property
    def amp(self) -> float:
        return self.__amp

    @property
    def samplerate(self) -> int:
        return self.__samplerate


class PureTone(Tone):
    """
    Wrapper class for generating pure tone.
    """
    def __init__(self,
                 freq: float,
                 duration: float,
                 amp: float = 1.0,
                 samplerate: int = 48000):
        self.__freq = freq
        self.__amp = amp
        self.__duration = duration
        self.__samplerate = samplerate
        self.__wave = self.__generate_wave()

    def hash(self) -> int:
        return hash(f"{self.freq} tone")

    @property
    def freq(self):
        return self.__freq

    def __generate_wave(self) -> Wave:
        tone = self.amp * sin(2.0 * pi * self.freq * arange(
            self.samplerate * self.duration) / self.samplerate).astype(float32)
        return tone

    def set_prop(self,
                 freq: Optional[float] = None,
                 duration: Optional[None] = None,
                 amp: Optional[float] = None,
                 samplerate: Optional[None] = None) -> None:
        if freq is not None:
            self.__freq = freq
        if duration is not None:
            self.__duration = duration
        if amp is not None:
            self.__amp = amp
        if samplerate is not None:
            self.__samplerate = samplerate
        self.__wave = self.__generate_wave()


def make_white_noise(duration: float, samplerate: int = 48000) -> Wave:
    array_length = int(48000 * duration)
    return uniform(-1, 1, array_length)


class Speaker(object):
    def __init__(self, device_index: int):
        self.__dev_idx = device_index

    @staticmethod
    def check_availbale_device():
        return query_devices()

    def play(self, tone: Tone, blocking=True, loop: bool = False) -> None:
        play(tone.wave,
             samplerate=tone.samplerate,
             blocking=blocking,
             loop=loop,
             device=self.__dev_idx)
        return None

    def stop(self, ignore_errors: bool = True):
        stop(ignore_errors=ignore_errors)
