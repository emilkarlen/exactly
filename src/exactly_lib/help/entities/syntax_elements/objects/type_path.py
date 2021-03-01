from pathlib import PurePosixPath
from typing import List, Sequence

from exactly_lib.common.help import documentation_text, headers
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args
from exactly_lib.definitions import instruction_arguments, formatting, misc_texts
from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId, \
    cross_reference_id_list
from exactly_lib.definitions.current_directory_and_path_type import path_type_path_rendering
from exactly_lib.definitions.doc_format import syntax_text
from exactly_lib.definitions.entity import syntax_elements, types, concepts
from exactly_lib.definitions.instruction_arguments import REL_SYMBOL_OPTION
from exactly_lib.definitions.path import HDS_DIR_DISPLAY_ORDER, SDS_DIR_DISPLAY_ORDER, REL_source_file_dir_OPTION
from exactly_lib.definitions.test_case.instructions import define_symbol
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.definitions.test_case.instructions.define_symbol import DEFINE_SYMBOL_INSTRUCTION_CROSS_REFERENCE
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help.entities.utils.se_within_parens import OptionallyWithinParens
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.tcfs.relative_path_options import REL_HDS_OPTIONS_MAP, \
    REL_SDS_OPTIONS_MAP, RelOptionInfo, REL_CWD_INFO
from exactly_lib.test_case import reserved_words
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render.cli_program_syntax import render_argument
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class _Documentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(syntax_elements.PATH_SYNTAX_ELEMENT)

        self._file_name = instruction_arguments.FILE_NAME_STRING
        self._relativity_name = instruction_arguments.RELATIVITY_ARGUMENT

        path_type_symbol = 'MY_PATH_SYMBOL'

        self._parser = TextParser({
            'Note': headers.NOTE_LINE_HEADER,
            'RELATIVITY_OPTION': self._relativity_name.name,
            'PATH_STRING': self._file_name.name,
            'posix_syntax': documentation_text.POSIX_SYNTAX,
            'string_type': formatting.keyword(types.STRING_TYPE_INFO.name.singular),
            'string_type_plain': types.STRING_TYPE_INFO.name,
            'reserved_word': misc_texts.RESERVED_WORD_NAME,
            'reserved_word_list_str': ', '.join([formatting.keyword(x) for x in reserved_words.RESERVED_TOKENS]),
            'path_type': formatting.keyword(types.PATH_TYPE_INFO.name.singular),
            'string_syntax_element': syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
            'cd': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
            'symbol': formatting.concept_(concepts.SYMBOL_CONCEPT_INFO),
            'SYMBOL_NAME': syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument.name,
            'define_symbol': formatting.InstructionName(instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME),
            'current_directory': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
            'REFERENCED_SYMBOL': path_type_symbol,
            'SYMBOL_REFERENCE': symbol_reference_syntax_for_name(path_type_symbol),
            'def_of_path_symbol': define_symbol.def_syntax_string(ValueType.PATH, path_type_symbol, '...'),
            'ref_of_path_symbol': '... ' + str(PurePosixPath(symbol_reference_syntax_for_name(path_type_symbol)) /
                                               'a' / 'path' / 'relative' / 'to' / path_type_symbol),
        })

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                cl_syntax.cl_syntax_for_args(self._cl_arguments())
            )
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return [
            self._file_name_string_sed(),
            self._relativity_sed(),
            self._symbol_name_sed(),
        ]

    def main_description_rest_paragraphs(self) -> List[ParagraphItem]:
        return []

    def main_description_rest_sub_sections(self) -> List[SectionItem]:
        return [
            docs.section(misc_texts.RELATIVITY.singular.capitalize(),
                         self._parser.fnap(_MAIN_DESCRIPTION_RELATIVITY),
                         [docs.section(headers.NOTES__HEADER__CAPITALIZED,
                                       self._parser.fnap(_MAIN_DESCRIPTION_RELATIVITY_NOTE))]),
            path_type_path_rendering()
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return cross_reference_id_list([
            concepts.TCDS_CONCEPT_INFO,
            concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO,
            concepts.SYMBOL_CONCEPT_INFO,
            syntax_elements.STRING_SYNTAX_ELEMENT,
            syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT,
            types.PATH_TYPE_INFO,
        ]) + [DEFINE_SYMBOL_INSTRUCTION_CROSS_REFERENCE]

    def _relativity_sed(self) -> SyntaxElementDescription:
        description_rest = self._parser.fnap(_RELATIVITY_DESCRIPTION_REST)
        description_rest.append(self._relativity_options_paragraph())

        return SyntaxElementDescription(self._relativity_name.name,
                                        description_rest)

    def _file_name_string_sed(self) -> SyntaxElementDescription:
        return SyntaxElementDescription(
            self._file_name.name,
            (),
            [invokation_variant_from_args([syntax_elements.STRING_SYNTAX_ELEMENT.single_mandatory])],
            self._parser.fnap(_STRING_DESCRIPTION_REST))

    def _symbol_name_sed(self) -> SyntaxElementDescription:
        return SyntaxElementDescription(syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.singular_name,
                                        self._parser.fnap(_SYMBOL_NAME_DESCRIPTION))

    def _cl_arguments(self) -> List[a.ArgumentUsage]:
        return [
            a.Single(a.Multiplicity.OPTIONAL,
                     self._relativity_name),
            a.Single(a.Multiplicity.MANDATORY,
                     self._file_name),

        ]

    def _relativity_options_paragraph(self) -> ParagraphItem:
        return docs.simple_list_with_space_between_elements_and_content([
            docs.list_item(
                self._options_for_directories_in_the(concepts.HDS_CONCEPT_INFO),
                self._options_for_directories_in_the_hds(),
            ),
            docs.list_item(
                self._options_for_directories_in_the(concepts.SDS_CONCEPT_INFO),
                self._options_for_directories_in_the_sds(),
            ),
            docs.list_item(
                self._parser.format('Option for {cd}'),
                self._options_for_current_directory(),
            ),
            docs.list_item(
                self._parser.format('Option for a path denoted by a {symbol}'),
                self._options_for_symbol(),
            ),
            docs.list_item(
                self._parser.format('Option for the location of the current source file'),
                self._options_for_rel_source_file(),
            ),
        ],
            docs.lists.ListType.ITEMIZED_LIST,
        )

    @staticmethod
    def _options_for_directories_in_the(directory_structure: SingularNameAndCrossReferenceId) -> str:
        return 'Options for directories in the ' + formatting.concept_(directory_structure)

    @staticmethod
    def _options_for_directories_in_the_hds() -> List[ParagraphItem]:
        return _options_for_directories_in_the_(REL_HDS_OPTIONS_MAP,
                                                HDS_DIR_DISPLAY_ORDER)

    @staticmethod
    def _options_for_directories_in_the_sds() -> List[ParagraphItem]:
        return _options_for_directories_in_the_(REL_SDS_OPTIONS_MAP,
                                                SDS_DIR_DISPLAY_ORDER)

    def _options_for_current_directory(self) -> List[ParagraphItem]:
        return ([
                    docs.first_row_is_header_table([
                        [docs.text_cell(REL_CWD_INFO.option_name_text)]
                    ])
                ]
                +
                self._parser.fnap(_REL_CD_DESCRIPTION)
                )

    def _options_for_symbol(self) -> List[ParagraphItem]:
        return ([
                    docs.first_column_is_header_table([
                        [
                            docs.text_cell(syntax_text(render_argument(REL_SYMBOL_OPTION))),
                        ]
                    ])
                ]
                +
                self._parser.fnap(_REL_SYMBOL_DESCRIPTION)
                )

    def _options_for_rel_source_file(self) -> List[ParagraphItem]:
        return ([
                    docs.first_column_is_header_table([
                        [
                            docs.text_cell(syntax_text(REL_source_file_dir_OPTION)),
                        ]
                    ])
                ]
                +
                self._parser.fnap(_REL_SOURCE_FILE_DESCRIPTION)
                )


DOCUMENTATION = OptionallyWithinParens(
    _Documentation(),
)


def _options_for_directories_in_the_(rel_opt_2_rel_option_info: dict,
                                     rel_opts_in_display_order: Sequence) -> List[ParagraphItem]:
    rows = list(map(lambda rel_opt: _mk_dir_info_row(rel_opt_2_rel_option_info[rel_opt]),
                    rel_opts_in_display_order))
    return [
        docs.first_column_is_header_table(rows)
    ]


def _mk_dir_info_row(dir_info: RelOptionInfo) -> list:
    return [
        docs.text_cell(dir_info.option_name_text),
        docs.text_cell(dir_info.informative_name),
    ]


_MAIN_DESCRIPTION_RELATIVITY = """\
If {PATH_STRING} is an absolute path, then {RELATIVITY_OPTION} must not be given.


If {PATH_STRING} is a relative path, then if {RELATIVITY_OPTION} is ...


  * given
  
    {PATH_STRING} is relative to the directory specified by {RELATIVITY_OPTION}

  * not given
  
    {PATH_STRING} is relative to the default relativity root directory,


The default relativity depends on the instruction,
and also on the argument's role in the instruction.
"""

_MAIN_DESCRIPTION_RELATIVITY_NOTE = """\
If {PATH_STRING} begins with a reference to a {path_type} {symbol},
then it is an absolute path.


For example:


```
{def_of_path_symbol}

{ref_of_path_symbol}
```
"""

_STRING_DESCRIPTION_REST = """\
A relative or absolute path, using {posix_syntax}.


{Note} The following {string_type_plain:s} are {reserved_word:s}: {reserved_word_list_str}.

To use any of them as a file name, it must be quoted.
"""

_RELATIVITY_DESCRIPTION_REST = """\
An option that specifies the directory that {PATH_STRING} is relative to.


The available relativities depends on the instruction,
and also on the argument's role in the instruction. 


Summary of options:
"""

_REL_CD_DESCRIPTION = """\
This options is needed since many instructions
have a default relativity other than the {cd}.
"""

_REL_SYMBOL_DESCRIPTION = """\
This option is always available.
"""

_REL_SOURCE_FILE_DESCRIPTION = """\
This option is only available when defining a path {symbol} using the {define_symbol} instruction.
"""

_SYMBOL_NAME_DESCRIPTION = """\
A {symbol} with type {path_type}.
"""
