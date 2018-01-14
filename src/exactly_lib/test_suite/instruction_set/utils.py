from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_parse import parse_token_on_current_line
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_suite.instruction_set import instruction
from exactly_lib.test_suite.instruction_set.instruction import FileNotAccessibleSimpleError

_WILDCARD_CHARACTERS = ('*', '?', '[')


class FileNamesResolver:
    def resolve(self, environment: instruction.Environment) -> list:
        raise NotImplementedError()


def parse_file_names_resolver(source: ParseSource) -> FileNamesResolver:
    token = parse_token_on_current_line(source, 'file name or glob pattern')
    source.consume_initial_space_on_current_line()
    if not source.is_at_eol:
        msg = 'Superfluous argument: `{}\''.format(source.remaining_part_of_current_line)
        raise SingleInstructionInvalidArgumentException(msg)
    source.consume_current_line()
    if token.is_quoted:
        return FileNamesResolverForPlainFileName(token.string)
    else:
        if is_wildcard_pattern(token.string):
            return FileNamesResolverForGlobPattern(token.string)
        else:
            return FileNamesResolverForPlainFileName(token.string)


class FileNamesResolverForPlainFileName(FileNamesResolver):
    def __init__(self, file_name: str):
        self.file_name = file_name

    def resolve(self, environment: instruction.Environment) -> list:
        path = environment.suite_file_dir_path / self.file_name
        if not path.is_file():
            raise FileNotAccessibleSimpleError(path)
        return [path]


class FileNamesResolverForGlobPattern(FileNamesResolver):
    def __init__(self, pattern: str):
        self.pattern = pattern

    def resolve(self, environment: instruction.Environment) -> list:
        paths = sorted(environment.suite_file_dir_path.glob(self.pattern))
        for path in paths:
            if not path.is_file():
                raise FileNotAccessibleSimpleError(path)
        return paths


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
