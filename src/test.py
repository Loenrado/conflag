import io
from enum import StrEnum, auto
from typing import Annotated

from conflag.decorator import command, register_sub_command
from conflag.run import run
from conflag.state.annotations import Argument, Option
from conflag.state.state import State


def test_run():
    app_state = State()

    is_run = [False, False]

    @command(app_state)
    def foo():
        is_run[0] = True

    @command(app_state)
    def bazz():
        is_run[1] = True

    assert is_run == [False, False]
    run(app_state, ["test.py", "foo"])
    assert is_run == [True, False]
    run(app_state, ["test.py", "bazz"])
    assert is_run == [True, True]


def test_run_with_name():
    app_state = State()

    is_run = [False]

    @command(app_state, "bazz")
    def foo():
        is_run[0] = True

    try:
        run(app_state, ["test.py", "foo"])
    except ValueError:
        pass
    else:
        assert False

    run(app_state, ["test.py", "bazz"])
    assert is_run[0]


def test_run_with_positional_argument():
    app_state = State()

    is_run = [False]

    @command(app_state)
    def foo(name):
        is_run[0] = True
        assert name == "bazz"

    run(app_state, ["test.py", "foo", "bazz"])
    assert is_run[0]


def test_run_with_positional_arguments():
    app_state = State()

    is_run = [False]

    @command(app_state)
    def foo(fee, fii, foo, fum):
        is_run[0] = True
        assert fee == "fee"
        assert fii == "fii"
        assert foo == "foo"
        assert fum == "fum"

    run(app_state, ["test.py", "foo", "fee", "fii", "foo", "fum"])
    assert is_run[0]


def test_run_with_too_many_positional_argument():
    app_state = State()

    is_run = [False]

    @command(app_state)
    def foo(name):
        is_run[0] = True
        assert name == "bazz"

    try:
        run(app_state, ["test.py", "foo", "bazz", "too_much"])
    except ValueError:
        pass
    else:
        assert False


def test_run_with_not_enough_positional_argument():
    app_state = State()

    is_run = [False]

    @command(app_state)
    def foo(name):
        is_run[0] = True
        assert name == "bazz"

    try:
        run(app_state, ["test.py", "foo"])
    except ValueError:
        pass
    else:
        assert False


def test_run_with_option():
    app_state = State()

    is_run = [False]

    @command(app_state)
    def foo(bazz="bar"):
        is_run[0] = True
        assert bazz == "bazz"

    run(app_state, ["test.py", "foo", "--bazz", "bazz"])
    assert is_run[0]


def test_run_with_positional_argument_and_option():
    app_state = State()

    is_run = [False]

    @command(app_state)
    def foo(fee, bazz="bar"):
        is_run[0] = True
        assert fee == "fee"
        assert bazz == "bazz"

    run(app_state, ["test.py", "foo", "--bazz", "bazz", "fee"])
    assert is_run[0]


def test_run_with_not_enough_positional_argument_and_option():
    app_state = State()

    is_run = [False]

    @command(app_state)
    def foo(fee, bazz="bar"):
        is_run[0] = True
        assert fee == "fee"
        assert bazz == "bazz"

    try:
        run(app_state, ["test.py", "foo", "--bazz", "bazz"])
    except ValueError:
        pass
    else:
        assert False


def test_run_with_positional_arguments_and_options():
    app_state = State()

    is_run = [False]

    @command(app_state)
    def foo(fee, fii, bazz="bar", bozz="bum"):
        is_run[0] = True
        assert fee == "fee"
        assert fii == "fii"
        assert bazz == "bar"
        assert bozz == "bozz"

    run(app_state, ["test.py", "foo", "--bozz", "bozz", "fee", "fii"])
    assert is_run[0]


def test_run_with_positional_argument_and_flags_at_end():
    app_state = State()

    is_run = [False]

    @command(app_state)
    def foo(fee, fii, bazz="bar", bozz="bum"):
        is_run[0] = True
        assert fee == "fee"
        assert fii == "fii"
        assert bazz == "bar"
        assert bozz == "bozz"

    run(app_state, ["test.py", "foo", "fee", "fii", "--bozz", "bozz"])
    assert is_run[0]


def test_run_with_substate():
    app_state = State()

    is_run = [False, False]

    @command(app_state)
    def foo(bar):
        is_run[0] = True
        assert bar == "bar"

    sub_state = State()

    @command(sub_state)
    def buzz(bee):
        is_run[1] = True
        assert bee == "bee"

    register_sub_command(app_state, sub_state, "sub")

    assert is_run == [False, False]
    run(app_state, ["test.py", "sub", "buzz", "bee"])
    assert is_run == [False, True]
    run(app_state, ["test.py", "foo", "bar"])
    assert is_run == [True, True]


def test_run_with_help():
    app_state = State()

    is_run = [False]

    @command(app_state)
    def foo(
        bar: str, bazz, filename: str = "test.txt", anotha="something else"
    ):
        is_run[1] = True
        assert bar == "bar"

    sub_state = State()

    @command(sub_state)
    def bar():
        pass

    register_sub_command(app_state, sub_state, "sub")

    ss = io.StringIO()
    run(app_state, ["test.py", "--help"], print_sink=ss)
    assert not is_run[0]

    run(app_state, ["test.py", "sub", "--help"], print_sink=ss)
    run(app_state, ["test.py", "sub", "bar", "--help"], print_sink=ss)
    run(app_state, ["test.py", "foo", "--help"], print_sink=ss)

    # print(ss.getvalue())


def test_run_command_with_help():
    app_state = State()

    is_run = [False]

    @command(app_state)
    def foo(
        bar: str,
        bazz,
        filename: str = "test.txt",
        anotha: str = "something else",
    ):
        is_run[1] = True
        assert bar == "bar"

    ss = io.StringIO()
    run(app_state, ["test.py", "foo", "--help"], print_sink=ss)
    assert not is_run[0]

    # print(ss.getvalue())


def test_run_with_choices_help():
    app_state = State()

    class Animal(StrEnum):
        DOG = auto()
        CAT = auto()
        TIGER = auto()

    @command(app_state)
    def foo(animal: Animal, backup: Animal = Animal.DOG):
        assert animal == Animal.CAT

    ss = io.StringIO()
    run(app_state, ["test.py", "foo", "--help"], print_sink=ss)
    run(app_state, ["test.py", "foo", "cat"])

    # print(ss.getvalue())


def test_run_with_config_file():
    config = {
        "global": "tomato",
        "foo": {
            "bar": "bazz",
        },
    }

    app_state = State(config=config)

    is_run = [False]

    @command(app_state)
    def foo(bar: str):
        is_run[0] = True
        assert bar == "bazz"
        assert app_state.config["global"] == "tomato"

    run(app_state, ["test.py", "foo"])
    assert is_run[0]


def test_run_with_config_file_override():
    config = {
        "global": "tomato",
        "foo": {
            "bar": "bazz",
        },
    }

    app_state = State(config=config)

    is_run = [False]

    @command(app_state)
    def foo(bar: str):
        is_run[0] = True
        assert bar == "bozz"
        assert app_state.config["global"] == "tomato"

    run(app_state, ["test.py", "foo", "bozz"])
    assert is_run[0]


def test_run_with_config_file_options():
    config = {
        "global": "tomato",
        "foo": {
            "bar": "bazz",
        },
    }

    app_state = State(config=config)

    is_run = [False]

    @command(app_state)
    def foo(bean: str, bar: str = "bozz"):
        is_run[0] = True
        assert bean == "bean"
        assert bar == "bazz"
        assert app_state["global"] == "tomato"

    run(app_state, ["test.py", "foo", "bean"])
    assert is_run[0]


def test_run_with_casting():
    app_state = State()

    is_run = [False]

    @command(app_state)
    def foo(
        bean: Annotated[int, Argument(caster=int)],
        opt: Annotated[int, Option(caster=int)] = 5,
    ):
        is_run[0] = True
        assert bean == 1
        assert opt == 7

    # run(app_state, ["test.py", "foo", "--help"])
    run(app_state, ["test.py", "foo", "--opt", "7", "1"])
    run(app_state, ["test.py", "foo", "1", "--opt", "7"])
    assert is_run[0]


test_run()
test_run_with_name()
test_run_with_positional_argument()
test_run_with_positional_arguments()
test_run_with_too_many_positional_argument()
test_run_with_not_enough_positional_argument()

test_run_with_option()
test_run_with_positional_argument_and_option()
test_run_with_not_enough_positional_argument_and_option()
test_run_with_positional_arguments_and_options()
test_run_with_positional_argument_and_flags_at_end()

test_run_with_substate()

test_run_with_help()
test_run_command_with_help()
test_run_with_choices_help()

test_run_with_config_file()
test_run_with_config_file_override()
test_run_with_config_file_options()

test_run_with_casting()
