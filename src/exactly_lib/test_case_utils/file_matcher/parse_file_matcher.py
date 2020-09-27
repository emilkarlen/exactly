from typing import List, Sequence

from exactly_lib.definitions import doc_format, matcher_model, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.definitions.primitives import file_matcher
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression import parser as ep
from exactly_lib.test_case_utils.expression.parser import GrammarParsers
from exactly_lib.test_case_utils.file_matcher import parse_dir_contents_model, file_or_dir_contents_doc
from exactly_lib.test_case_utils.file_matcher.impl import \
    regular_file_contents, dir_contents, file_contents_utils
from exactly_lib.test_case_utils.file_matcher.impl.file_type import FileMatcherType
from exactly_lib.test_case_utils.file_matcher.impl.name import \
    glob_pattern as name__glob_pattern, reg_ex as name__reg_ex
from exactly_lib.test_case_utils.file_matcher.impl.path import \
    glob_pattern as path__glob_pattern, reg_ex as path__reg_ex
from exactly_lib.test_case_utils.file_matcher.impl.run_program import parse as parse_run
from exactly_lib.test_case_utils.file_matcher.impl.run_program.doc import RunSyntaxDescription
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.matcher import standard_expression_grammar
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
from exactly_lib.type_system.logic.file_matcher import FileMatcherSdv, FileMatcher
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.table import TableCell
from exactly_lib.util.textformat.textformat_parser import TextParser
from .impl.utils import glob_or_regex

NAME_MATCHER_ARGUMENT = syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.argument

TYPE_MATCHER_ARGUMENT = a.Named('TYPE')

_NAME_PARSER = glob_or_regex.parser(
    name__glob_pattern.parse,
    name__reg_ex.parse,
)

_PATH_PARSER = glob_or_regex.parser(
    path__glob_pattern.parse,
    path__reg_ex.parse,
)


def parsers(must_be_on_current_line: bool = False) -> GrammarParsers[FileMatcherSdv]:
    return _PARSERS_FOR_MUST_BE_ON_CURRENT_LINE[must_be_on_current_line]


def _parse_type_matcher(parser: TokenParser) -> FileMatcherSdv:
    file_type = parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE,
        file_properties.SYNTAX_TOKEN_2_FILE_TYPE.get,
        TYPE_MATCHER_ARGUMENT.name)
    return sdv_components.matcher_sdv_from_constant_primitive(FileMatcherType(file_type))


def _parse_regular_file_contents(token_parser: TokenParser) -> FileMatcherSdv:
    string_matcher = parse_string_matcher.parsers().simple.parse_from_token_parser(token_parser)
    return regular_file_contents.sdv(string_matcher)


def _parse_dir_contents(token_parser: TokenParser) -> FileMatcherSdv:
    from exactly_lib.test_case_utils.files_matcher import parse_files_matcher
    model_constructor = DIR_CONTENTS_MODEL_PARSER.parse(token_parser)
    files_matcher = parse_files_matcher.parsers().simple.parse_from_token_parser(token_parser)
    return dir_contents.dir_matches_files_matcher_sdv(model_constructor,
                                                      files_matcher)


def _constant(matcher: FileMatcher) -> FileMatcherSdv:
    return sdv_components.matcher_sdv_from_constant_primitive(matcher)


def _file_types_table() -> docs.ParagraphItem:
    def row(type_name: str, description: str) -> List[TableCell]:
        return [
            docs.cell(docs.paras(doc_format.enum_name_text(type_name))),
            docs.cell(_TP.fnap(description)),
        ]

    return docs.plain_table([
        row(type_info.type_argument, 'File must be a ' + type_info.description)
        for type_info in sorted(file_properties.TYPE_INFO.values(),
                                key=lambda ti: ti.type_argument)
    ])


class _NameSyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [glob_or_regex.GLOB_OR_REGEX__ARG_USAGE]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_NAME_MATCHER_SED_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT,
            syntax_elements.REGEX_SYNTAX_ELEMENT,
        ])


class _PathSyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [glob_or_regex.GLOB_OR_REGEX__ARG_USAGE]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_PATH_MATCHER_SED_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT,
            syntax_elements.REGEX_SYNTAX_ELEMENT,
        ])


class _TypeSyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Single(a.Multiplicity.MANDATORY,
                     TYPE_MATCHER_ARGUMENT)
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _type_matcher_sed_description()


GRAMMAR = standard_expression_grammar.new_grammar(
    concept=grammar.Concept(
        name=types.FILE_MATCHER_TYPE_INFO.name,
        type_system_type_name=types.FILE_MATCHER_TYPE_INFO.identifier,
        syntax_element_name=syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.argument,
    ),
    model=matcher_model.FILE_MATCHER_MODEL,
    value_type=ValueType.FILE_MATCHER,
    simple_expressions=(
        NameAndValue(
            file_matcher.NAME_MATCHER_NAME,
            grammar.Primitive(
                _NAME_PARSER.parse,
                _NameSyntaxDescription()
            )
        ),

        NameAndValue(
            file_matcher.PATH_MATCHER_NAME,
            grammar.Primitive(
                _PATH_PARSER.parse,
                _PathSyntaxDescription()
            )
        ),

        NameAndValue(
            file_matcher.TYPE_MATCHER_NAME,
            grammar.Primitive(
                _parse_type_matcher,
                _TypeSyntaxDescription()
            )
        ),

        NameAndValue(
            file_check_properties.REGULAR_FILE_CONTENTS,
            grammar.Primitive(
                _parse_regular_file_contents,
                file_contents_utils.FileContentsSyntaxDescription(
                    file_or_dir_contents_doc.REGULAR_FILE_DOCUMENTATION_SETUP
                )
            )
        ),

        NameAndValue(
            file_check_properties.DIR_CONTENTS,
            grammar.Primitive(
                _parse_dir_contents,
                file_contents_utils.FileContentsSyntaxDescription(
                    file_or_dir_contents_doc.DIR_DOCUMENTATION
                )
            )
        ),

        NameAndValue(
            file_matcher.PROGRAM_MATCHER_NAME,
            grammar.Primitive(
                parse_run.parse,
                RunSyntaxDescription(),
            )
        ),
    ),
)

_PARSERS_FOR_MUST_BE_ON_CURRENT_LINE = ep.parsers_for_must_be_on_current_line(GRAMMAR)

_TP = TextParser({
    'MATCHER': types.FILE_MATCHER_TYPE_INFO.name.singular,
    'TYPE': TYPE_MATCHER_ARGUMENT.name,
    'SYMLINK_TYPE': file_properties.TYPE_INFO[FileType.SYMLINK].type_argument,
    'GLOB_PATTERN_INFORMATIVE_NAME': syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.single_line_description_str,
    'REG_EX_PATTERN_INFORMATIVE_NAME': syntax_elements.REGEX_SYNTAX_ELEMENT.single_line_description_str,
    'MODEL': matcher_model.FILE_MATCHER_MODEL,
    'SYMBOLIC_LINKS_ARE_FOLLOWED': misc_texts.SYMBOLIC_LINKS_ARE_FOLLOWED,
})

DIR_CONTENTS_MODEL_PARSER = parse_dir_contents_model.Parser()

_NAME_MATCHER_SED_DESCRIPTION = """\
Matches {MODEL:s} who's final path component (base name) matches


  * {GLOB_PATTERN_INFORMATIVE_NAME}, or
  
  
  * {REG_EX_PATTERN_INFORMATIVE_NAME}
"""

_PATH_MATCHER_SED_DESCRIPTION = """\
Matches {MODEL:s} who's absolute path matches


  * {GLOB_PATTERN_INFORMATIVE_NAME}, that matches the last components of the path, or
  
  
  * {REG_EX_PATTERN_INFORMATIVE_NAME}
"""


def _type_matcher_sed_description() -> List[docs.ParagraphItem]:
    return (
            _TP.fnap(_TYPE_MATCHER__BEFORE_TYPE_LIST) +
            [_file_types_table()] +
            _TP.fnap(_TYPE_MATCHER__AFTER_TYPE_LIST)
    )


_TYPE_MATCHER__BEFORE_TYPE_LIST = """\
Matches {MODEL:s} who's type is {TYPE}.


{TYPE} is one of:
"""

_TYPE_MATCHER__AFTER_TYPE_LIST = """\
{SYMBOLIC_LINKS_ARE_FOLLOWED} (unless matched type is {SYMLINK_TYPE}).
"""
