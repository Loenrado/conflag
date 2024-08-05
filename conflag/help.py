from typing import Annotated, Optional, Union, get_args, get_origin

from conflag.state.command import Command
from conflag.state.state import State


def help(x: Union[State, Command], print_sink):
    match x:
        case State():
            help_state(x, print_sink)
        case Command():
            help_command(x, print_sink)


def help_state(state: State, print_sink):
    output = "HELP\n"

    output += "\nCOMMANDS:\n"
    for name in state.sub_states.keys():
        output += f"\t\t {name}\n"

    for command in state.commands.values():
        output += f"\t\t {command.name}\n"

    output += "\n"
    print(output, file=print_sink)


def help_command(command: Command, print_sink):
    output = f"USAGE: {command.name} [OPTIONS] <ARGUMENTS>\n"

    output += "\nOPTIONS:\n"
    for option in command.options.values():
        choices = get_choices(option.type_hint)
        output += (
            f"\t--{option.name}".rjust(10)
            + f": {get_type_hint_name(option.type_hint)}".ljust(10)
            + f"default={option.default}".ljust(20)
            + (f"choices={choices}" if choices else "")
            + "\n"
        )

    output += "\nARGUMENTS:\n"
    for positional_argument in command.positional_arguments.values():
        choices = get_choices(positional_argument.type_hint)
        output += (
            f"\t{positional_argument.name}".rjust(10)
            + f": {get_type_hint_name(positional_argument.type_hint)}".ljust(10)
            + (f"choices={choices}" if choices else "")
            + "\n"
        )

    output += "\n"
    print(output, file=print_sink)


def get_type_hint_name(type_hint):
    return (
        type_hint.__name__
        if get_origin(type_hint) is not Annotated
        else get_args(type_hint)[0].__name__
    )


def get_choices(type_hint):
    try:
        return ", ".join(choice for choice in type_hint)
    except TypeError:
        return
