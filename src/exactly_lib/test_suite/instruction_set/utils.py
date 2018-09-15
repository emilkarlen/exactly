from pathlib import Path
from typing import List, Iterable, Callable

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_parse import parse_token_on_current_line
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_suite.instruction_set import instruction
from exactly_lib.test_suite.instruction_set.instruction import FileNotAccessibleSimpleError

_WILDCARD_CHARACTERS = ('*', '?', '[')


class FileNamesResolver:
    def resolve(self, environment: instruction.Environment) -> List[Path]:
        raise NotImplementedError()


SinglePathResolver = Callable[[Path], Path]


def single_regular_file_resolver(path: Path) -> Path:
    if path.is_file():
        return path
    raise FileNotAccessibleSimpleError(path)


def parse_file_names_resolver(source: ParseSource,
                              path_resolver: SinglePathResolver = single_regular_file_resolver) -> FileNamesResolver:
    token = parse_token_on_current_line(source, 'file name or glob pattern')
    source.consume_initial_space_on_current_line()
    if not source.is_at_eol:
        msg = 'Superfluous argument: `{}\''.format(source.remaining_part_of_current_line)
        raise SingleInstructionInvalidArgumentException(msg)
    source.consume_current_line()
    if token.is_quoted:
        return FileNamesResolverForPlainFileName(path_resolver, token.string)
    else:
        if is_wildcard_pattern(token.string):
            return FileNamesResolverForGlobPattern(path_resolver, token.string)
        else:
            return FileNamesResolverForPlainFileName(path_resolver, token.string)


class FileNamesResolverForPlainFileName(FileNamesResolver):
    def __init__(self,
                 path_resolver: SinglePathResolver,
                 file_name: str,
                 ):
        self.path_resolver = path_resolver
        self.file_name = file_name

    def resolve(self, environment: instruction.Environment) -> List[Path]:
        path = environment.suite_file_dir_path / self.file_name
        return [self.path_resolver(path)]


class FileNamesResolverForGlobPattern(FileNamesResolver):
    def __init__(self,
                 path_resolver: SinglePathResolver,
                 pattern: str
                 ):
        self.path_resolver = path_resolver
        self.pattern = pattern

    def resolve(self, environment: instruction.Environment) -> List[Path]:
        paths = environment.suite_file_dir_path.glob(self.pattern)
        return sorted([
            self.path_resolver(path)
            for path in paths
        ])


def is_wildcard_pattern(instruction_text: str) -> bool:
    return _contains_any_of(_WILDCARD_CHARACTERS, instruction_text)


def _contains_any_of(strings_looking_for: Iterable[str], string_looking_in: str) -> bool:
    for string_looking_for in strings_looking_for:
        if string_looking_in.find(string_looking_for) != -1:
            return True
    return False
