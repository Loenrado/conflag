import re
import sys

from conflag.help import help
from conflag.state.command import Command
from conflag.state.state import State

FLAG = re.compile(r"--(\S*)")


def run(
    state: State,
    cli_arguments: list[str] = sys.argv,
    print_sink=None,
):
    # get rid of the first cli_argument that is unused.
    _run(state, cli_arguments[1:], print_sink)


def _run(state: State, cli_arguments: list[str], print_sink):
    if len(cli_arguments) == 0:
        raise ValueError("not enough cli arguments")

    if sub_state := state.sub_states.get(cli_arguments[0]):
        return _run(sub_state, cli_arguments[1:], print_sink)

    elif command := state.commands.get(cli_arguments[0]):
        return run_command(state, command, cli_arguments, print_sink)

    elif match := FLAG.match(cli_arguments[0]):
        if match[1] == "help":
            return help(state, print_sink)

    raise ValueError("command %s not found", cli_arguments[0])


def run_command(
    state: State,
    command: Command,
    cli_arguments: list[str],
    print_sink,
):
    parameters = get_default_parameters(state, command)
    casters = get_casters(command)

    positional_argument_gen = (
        positional_argument
        for positional_argument in command.positional_arguments.values()
    )

    cli_argument_gen = (cli_argument for cli_argument in cli_arguments[1:])

    for cli_argument in cli_argument_gen:
        if match := FLAG.match(cli_argument):
            # option
            name = match[1]
            if name == "help":
                help(
                    command,
                    print_sink,
                )
                return

            if name not in parameters:
                raise ValueError(
                    "parameter name %s does not exist for command %s",
                    name,
                    command.name,
                )

            value = next(cli_argument_gen)
            parameters[name] = casters[name](value)
        else:
            try:
                name = next(positional_argument_gen).name
                parameters[name] = casters[name](cli_argument)
            except StopIteration:
                raise ValueError("wrong number of parameters")

    if len(parameters) != len(command.positional_arguments) + len(
        command.options
    ):
        raise ValueError("wrong number of parameters")

    return command.func(**parameters)


def get_default_parameters(state: State, command: Command):
    options_from_defaults = {k: v.default for k, v in command.options.items()}
    options_from_config = (
        {
            k: v
            for k, v in state.config[command.name].items()
            if k in command.options
        }
        if command.name in state.config
        else {}
    )
    positional_arguments_from_config = (
        {
            k: v
            for k, v in state.config[command.name].items()
            if k in command.positional_arguments
        }
        if command.name in state.config
        else {}
    )

    return (
        options_from_defaults
        | options_from_config
        | positional_arguments_from_config
    )


def get_casters(command: Command):
    return {k: v.caster for k, v in command.options.items()} | {
        k: v.caster for k, v in command.positional_arguments.items()
    }
