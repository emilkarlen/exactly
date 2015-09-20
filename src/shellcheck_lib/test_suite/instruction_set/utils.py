from shellcheck_lib.test_suite.instruction_set import instruction
from shellcheck_lib.test_suite.instruction_set.instruction import FileNotAccessibleSimpleError

_WILDCARD_CHARACTERS = ('*', '?', '[')


def resolve_non_wildcard_path(file_name: str, environment: instruction.Environment) -> list:
    path = environment.suite_file_dir_path / file_name
    if not path.is_file():
        raise FileNotAccessibleSimpleError(path)
    return [path]


def resolve_wildcard_paths(pattern: str, environment: instruction.Environment) -> list:
    paths = sorted(environment.suite_file_dir_path.glob(pattern))
    for path in paths:
        if not path.is_file():
            raise FileNotAccessibleSimpleError(path)
    return paths


def is_wildcard_pattern(instruction_text: str) -> bool:
    return _contains_any_of(_WILDCARD_CHARACTERS, instruction_text)


def _contains_any_of(strings_looking_for: tuple, string_looking_in: str):
    for string_looking_for in strings_looking_for:
        if string_looking_in.find(string_looking_for) != -1:
            return True
    return False
