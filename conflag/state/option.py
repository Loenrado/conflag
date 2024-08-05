from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Option:
    name: str
    default: Any
    type_hint: Any
    caster: Callable[[str], Any] = field(default=lambda x: x)
