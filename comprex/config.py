import argparse as ap
from typing import Any, Dict, List

import yaml

Settings = Dict[str, Any]
# Alias for settings
Comport = Settings
Experimental = Settings
Metadata = Settings
PinMode = Dict[int, str]


class Config(dict):
    def __init__(self, path: str) -> None:
        f = open(path, "r")
        self.__path = path
        d: dict = yaml.safe_load(f)
        [self.__setitem__(item[0], item[1]) for item in d.items()]
        f.close()

    def __missing__(self) -> Settings:
        return dict()

    @property
    def comport(self) -> Comport:
        return self["Comport"]

    @property
    def experimental(self) -> Experimental:
        return self["Experimental"]

    @property
    def metadata(self) -> Metadata:
        return self["Metadata"]

    @property
    def pinmode(self) -> PinMode:
        return self["PinMode"]


class PinoClap(object):
    def __init__(self):
        self.__parser = ap.ArgumentParser(description="About this program")
        self.__parser.add_argument("--yaml",
                                   "-y",
                                   help="About this argument",
                                   type=str)
        self.__parser.add_argument("--yamls",
                                   "-Y",
                                   help="About this argument",
                                   nargs="*")
        self.__parser.add_argument("--port",
                                   "-p",
                                   help="About this argument",
                                   type=str)
        self.__parser.add_argument("--baudrate",
                                   "-b",
                                   help="About this argument",
                                   type=int)
        self.__parser.add_argument("--dotino",
                                   "-d",
                                   help="About this argument",
                                   type=str)
        self.__parser.add_argument("--timeout",
                                   "-t",
                                   help="About this argument",
                                   type=float)
        self.__parser.add_argument("--warmup",
                                   "-w",
                                   help="About this argument",
                                   type=float)
        self.__parser.add_argument("--arduino",
                                   "-a",
                                   help="About this argument",
                                   type=str)
        self.__args = self.__parser.parse_args()

    @property
    def config(self) -> Config:
        return Config(self.__args.yaml)

    @property
    def configs(self) -> List[Config]:
        return [Config(yml) for yml in self.__args.yamls]

    @property
    def port(self) -> str:
        return self.__args.port

    @property
    def baudrate(self) -> int:
        return self.__args.baudrate

    @property
    def dotino(self) -> str:
        return self.__args.dotino

    @property
    def timeout(self) -> float:
        return self.__args.timeout

    @property
    def warmup(self) -> float:
        return self.__args.warmup

    @property
    def arduino(self) -> str:
        return self.__args.arduino
