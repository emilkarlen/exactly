from exactly_lib.act_phase_setups import command_line


def shell_command_source_line_for(command: str) -> str:
    return command_line.SHELL_COMMAND_MARKER + ' ' + command
