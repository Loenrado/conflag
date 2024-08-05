from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass

from conflag.state.argument import Argument
from conflag.state.option import Option


@dataclass
class Command:
    name: str
    func: Callable
    positional_arguments: OrderedDict[str, Argument]
    options: dict[str, Option]
