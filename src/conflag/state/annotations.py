from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Option:
    caster: Optional[Callable[[str], Any]] = None


@dataclass
class Argument:
    caster: Optional[Callable[[str], Any]] = None
