from exactly_lib.actors import common


def shell_command_source_line_for(command: str) -> str:
    return common.SHELL_COMMAND_MARKER + ' ' + command