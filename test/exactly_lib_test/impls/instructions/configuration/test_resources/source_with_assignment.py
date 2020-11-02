from exactly_lib.definitions import instruction_arguments


def syntax_for_assignment_of(value: str) -> str:
    return instruction_arguments.ASSIGNMENT_OPERATOR + ' ' + value
