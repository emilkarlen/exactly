from typing import List, Sequence

from exactly_lib.definitions import doc_format, matcher_model, misc_texts
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.definitions.primitives import file_matcher
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.expression import parser as ep
from exactly_lib.impls.types.expression.parser import GrammarParsers
from exactly_lib.impls.types.file_matcher import parse_dir_contents_model, file_or_dir_contents_doc
from exactly_lib.impls.types.file_matcher.impl import \
    regular_file_contents, dir_contents, file_contents_utils
from exactly_lib.impls.types.file_matcher.impl.file_type import FileMatcherType
from exactly_lib.impls.types.file_matcher.impl.run_program import parse as parse_run
from exactly_lib.impls.types.file_matcher.impl.run_program.doc import RunSyntaxDescription
from exactly_lib.impls.types.matcher import standard_expression_grammar
from exactly_lib.impls.types.matcher.impls import sdv_components, combinator_matchers
from exactly_lib.impls.types.string_matcher import parse_string_matcher
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.file_matcher import FileMatcherSdv
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcher
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.structure.table import TableCell
from exactly_lib.util.textformat.textformat_parser import TextParser
from .impl.names import parsers as names_parsers, doc as names_doc
from ... import file_properties

NAME_MATCHER_ARGUMENT = syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.argument

TYPE_MATCHER_ARGUMENT = a.Named('TYPE')


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
    from exactly_lib.impls.types.files_matcher import parse_files_matcher
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


def _description() -> SectionContents:
    return SectionContents(
        [],
        [names_doc.name_parts_description()],
    )


GRAMMAR = standard_expression_grammar.new_grammar(
    concept=grammar.Concept(
        name=types.FILE_MATCHER_TYPE_INFO.name,
        type_system_type_name=types.FILE_MATCHER_TYPE_INFO.identifier,
        syntax_element_name=syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.argument,
    ),
    description=_description,
    model=matcher_model.FILE_MATCHER_MODEL,
    value_type=ValueType.FILE_MATCHER,
    simple_expressions=(

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

        NameAndValue(
            file_matcher.WHOLE_PATH_MATCHER_NAME,
            grammar.Primitive(
                names_parsers.WHOLE_PATH_PARSER.parse,
                names_doc.whole_path_syntax_description()
            )
        ),

        NameAndValue(
            file_matcher.NAME_MATCHER_NAME,
            grammar.Primitive(
                names_parsers.NAME_PARSER.parse,
                names_doc.name_syntax_description()
            )
        ),

        NameAndValue(
            file_matcher.STEM_MATCHER_NAME,
            grammar.Primitive(
                names_parsers.STEM_PARSER.parse,
                names_doc.stem_syntax_description(file_matcher.STEM_MATCHER_NAME)
            )
        ),

        NameAndValue(
            file_matcher.SUFFIXES_MATCHER_NAME,
            grammar.Primitive(
                names_parsers.SUFFIXES_PARSER.parse,
                names_doc.suffixes_syntax_description(file_matcher.SUFFIXES_MATCHER_NAME)
            )
        ),

        NameAndValue(
            file_matcher.SUFFIX_MATCHER_NAME,
            grammar.Primitive(
                names_parsers.SUFFIX_PARSER.parse,
                names_doc.suffix_syntax_description(file_matcher.SUFFIX_MATCHER_NAME)
            )
        ),
    ),
    model_freezer=combinator_matchers.no_op_freezer,
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
{SYMBOLIC_LINKS_ARE_FOLLOWED} (unless {TYPE} is {SYMLINK_TYPE}).
"""
