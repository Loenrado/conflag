from dataclasses import dataclass, field
from typing import Any, Optional, Self

from conflag.state.command import Command


@dataclass
class State:
    config: dict[str, Any] = field(default_factory=dict)
    commands: dict[str, Command] = field(default_factory=dict)
    sub_states: dict[str, Self] = field(default_factory=dict)

    def __getitem__(self, key):
        return self.config[key]
