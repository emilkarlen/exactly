from typing import Sequence, List, Callable

from exactly_lib.definitions import doc_format
from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import file_matcher
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.file_matcher.impl.names import defs
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import Section
from exactly_lib.util.textformat.textformat_parser import TextParser


def name_syntax_description() -> grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken:
    return _SyntaxDescription(_TP.fnap__fun(_NAME_MATCHER_SED_DESCRIPTION))


def stem_syntax_description(part_name: str) -> grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken:
    return _SyntaxDescription(_name_part_description(part_name, FileNames.get_stem))


def suffixes_syntax_description(part_name: str) -> grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken:
    return _SyntaxDescription(_name_part_description(part_name, FileNames.get_suffixes))


def suffix_syntax_description(part_name: str) -> grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken:
    return _SyntaxDescription(_name_part_description(part_name, FileNames.get_suffix))


def whole_path_syntax_description() -> grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken:
    return _SyntaxDescription(_TP.fnap__fun(_PATH_MATCHER_SED_DESCRIPTION))


def name_parts_description() -> Section:
    return Section(
        docs.text('File name parts'),
        docs.SectionContents(
            [_name_parts_table()]
        )
    )


class _SyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    def __init__(self, get_description: Callable[[], List[ParagraphItem]]):
        self._get_description = get_description

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [defs.GLOB_OR_REGEX__ARG_USAGE]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return self._get_description()

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT,
            syntax_elements.REGEX_SYNTAX_ELEMENT,
        ])


class FileNames:
    def __init__(self,
                 name: str,
                 stem: str,
                 suffixes: str,
                 suffix: str,
                 ):
        self.path = '/dir/' + name
        self.name = name
        self.stem = stem
        self.suffixes = suffixes
        self.suffix = suffix

    def get_stem(self) -> str:
        return self.stem

    def get_suffixes(self) -> str:
        return self.suffixes

    def get_suffix(self) -> str:
        return self.suffix

    @staticmethod
    def of_eq_suffix_es(
            name: str,
            stem: str,
            suffix_es: str,
    ) -> 'FileNames':
        return FileNames(name, stem, suffix_es, suffix_es)


_FILE_NAMES_EXAMPLE = FileNames(
    'a.tar.gz',
    'a',
    '.tar.gz',
    '.gz',
)


def _name_parts_table() -> docs.ParagraphItem:
    def cell_of_name_part_name(text: str) -> docs.TableCell:
        return docs.cell([docs.para(text)])

    def cell_of_literal(text: str) -> docs.TableCell:
        return docs.cell([docs.para(doc_format.literal_text(text))])

    def row_of(names: FileNames) -> List[docs.TableCell]:
        return [
            cell_of_literal(value)
            for value in [
                names.path,
                names.name,
                names.stem,
                names.suffixes,
                names.suffix,
            ]
        ]

    header_row = [
        cell_of_name_part_name(header)
        for header in [
            file_matcher.WHOLE_PATH_MATCHER_NAME,
            file_matcher.NAME_MATCHER_NAME,
            file_matcher.STEM_MATCHER_NAME,
            file_matcher.SUFFIXES_MATCHER_NAME,
            file_matcher.SUFFIX_MATCHER_NAME,
        ]
    ]

    return docs.first_row_is_header_table(
        [header_row] +
        [row_of(example) for example in file_name_examples()]
    )


def file_name_examples() -> Sequence[FileNames]:
    return [
        _FILE_NAMES_EXAMPLE,
        FileNames.of_eq_suffix_es('f.txt', 'f', '.txt'),
        FileNames.of_eq_suffix_es(
            'f',
            stem='f',
            suffix_es='',
        ),
        FileNames.of_eq_suffix_es(
            'f.',
            stem='f',
            suffix_es='.',
        ),
        FileNames(
            '.x.y',
            stem='',
            suffixes='.x.y',
            suffix='.y',
        ),
    ]


def _name_part_description(part_primitive: str,
                           get_part: Callable[[FileNames], str],
                           ) -> Callable[[], List[ParagraphItem]]:
    tp = TextParser({
        'MODEL': matcher_model.FILE_MATCHER_MODEL,
        'name': file_matcher.NAME_MATCHER_NAME,
        'part': part_primitive,
        'example_name': _FILE_NAMES_EXAMPLE.name,
        'example_part': get_part(_FILE_NAMES_EXAMPLE),
    })

    return tp.fnap__fun(_NAME_PART_DESCRIPTION)


_TP = TextParser({
    'GLOB_PATTERN': syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.singular_name,
    'REG_EX': syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name,
    'MODEL': matcher_model.FILE_MATCHER_MODEL,
})

_NAME_PART_DESCRIPTION = """\
Matches {MODEL:s} who's "{part}" part of its {name} matches the given pattern.


E.g., the {part} of '{example_name}' is '{example_part}'.
"""

_NAME_MATCHER_SED_DESCRIPTION = """\
Matches {MODEL:s} who's final path component (base name) matches the given pattern.
"""

_PATH_MATCHER_SED_DESCRIPTION = """\
Matches {MODEL:s} who's absolute path matches the given pattern.
"""
