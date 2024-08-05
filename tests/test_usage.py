import json
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Annotated

from conflag import command, register_sub_command, run
from conflag.state import Argument, State

with open("tests/config.json", "r") as f:
    d = json.load(f)

app_state = State(config=d)

sub_state = State()
register_sub_command(app_state, sub_state, "within")


@command(sub_state)
def sub(something="nothing"):
    print(something)


@dataclass
class Dog:
    age: int
    breed: str

    @staticmethod
    def from_str(s: str):
        age, breed = tuple(s.split(","))
        return Dog(int(age), breed)


@command(app_state)
def foo():
    print("Hello world!")


@command(app_state)
def bar(dog: Annotated[Dog, Argument(caster=Dog.from_str)]):
    print(dog)


class Breeds(StrEnum):
    GOLDEN_RETRIEVER = auto()
    LAB = auto()
    LILY = auto()


@command(app_state)
def bazz(breed: Breeds):
    print(breed)


if __name__ == "__main__":
    run(app_state)
