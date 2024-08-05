import inspect
from collections import OrderedDict
from collections.abc import Callable
from functools import wraps
from typing import Annotated, Optional, get_args, get_origin

from conflag.state.annotations import Argument as AnnotatedArgument
from conflag.state.annotations import Option as AnnotatedOption
from conflag.state.argument import Argument
from conflag.state.command import Command
from conflag.state.option import Option
from conflag.state.state import State


def command(state: State, name: Optional[str] = None):
    def decorator(func: Callable):
        register_command(state, name, func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        return wrapper

    return decorator


def register_command(
    state: State, command_name: Optional[str], func: Callable
):
    if command_name is None:
        command_name = func.__name__

    signature = inspect.signature(func)
    parameters = signature.parameters

    positional_arguments = OrderedDict()
    for argument_name, parameter in parameters.items():
        if parameter.default is inspect.Signature.empty:
            positional_arguments[argument_name] = Argument(
                argument_name, **parse_annotation(parameter.annotation)
            )

    options = {
        name: Option(
            name, parameter.default, **parse_annotation(parameter.annotation)
        )
        for name, parameter in parameters.items()
        if parameter.default is not inspect.Signature.empty
    }

    state.commands[command_name] = Command(
        command_name, func, positional_arguments, options
    )


def parse_annotation(annotation):
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        return {"type_hint": args[0], **parse_annotated_args(args)}
    return {"type_hint": annotation}


def parse_annotated_args(args):
    for arg in args:
        match arg:
            case AnnotatedArgument() | AnnotatedOption():
                if arg.caster:
                    return {"caster": arg.caster}
    return {}


def register_sub_command(state: State, sub_state: State, name: str):
    state.sub_states[name] = sub_state
