from exactly_lib.common.help import documentation_text
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help_texts import instruction_arguments, formatting
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId, cross_reference_id_list
from exactly_lib.help_texts.doc_format import syntax_text
from exactly_lib.help_texts.entity import syntax_elements, types, concepts
from exactly_lib.help_texts.file_ref import HDS_DIR_DISPLAY_ORDER, SDS_DIR_DISPLAY_ORDER
from exactly_lib.help_texts.instruction_arguments import REL_SYMBOL_OPTION
from exactly_lib.test_case_file_structure.relative_path_options import REL_HOME_OPTIONS_MAP, \
    REL_SDS_OPTIONS_MAP, RelOptionInfo, REL_CWD_INFO
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render.cli_program_syntax import render_argument
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class _Documentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(TypeCategory.DATA,
                         syntax_elements.PATH_SYNTAX_ELEMENT)

        self._string_name = a.Named(syntax_elements.STRING_SYNTAX_ELEMENT.singular_name)
        self._relativity_name = instruction_arguments.RELATIVITY_ARGUMENT

        self._parser = TextParser({
            'RELATIVITY_OPTION': self._relativity_name.name,
            'PATH_STRING': self._string_name.name,
            'posix_syntax': documentation_text.POSIX_SYNTAX,
            'string_type': formatting.keyword(types.STRING_TYPE_INFO.name.singular),
            'path_type': formatting.keyword(types.PATH_TYPE_INFO.name.singular),
            'string_syntax_element': syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
            'cd': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
            'symbol': formatting.concept_(concepts.SYMBOL_CONCEPT_INFO),
            'SYMBOL_NAME': syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument.name,
        })

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                cl_syntax.cl_syntax_for_args(self._cl_arguments())
            )
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            self._string_sed(),
            self._relativity_sed(),
            self._symbol_name_sed(),
        ]

    def main_description_rest_paragraphs(self) -> list:
        return self._parser.fnap(_MAIN_DESCRIPTION_REST)

    def see_also_targets(self) -> list:
        return cross_reference_id_list([
            concepts.TEST_CASE_DIRECTORY_STRUCTURE_CONCEPT_INFO,
            concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO,
            concepts.SYMBOL_CONCEPT_INFO,
            syntax_elements.STRING_SYNTAX_ELEMENT,
            syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT,
            types.PATH_TYPE_INFO,
        ])

    def _relativity_sed(self) -> SyntaxElementDescription:
        description_rest = self._parser.fnap(_RELATIVITY_DESCRIPTION_REST)
        description_rest.append(self._relativity_options_paragraph())

        return SyntaxElementDescription(self._relativity_name.name,
                                        description_rest)

    def _string_sed(self) -> SyntaxElementDescription:
        return SyntaxElementDescription(self._string_name.name,
                                        self._parser.fnap(_STRING_DESCRIPTION_REST))

    def _symbol_name_sed(self) -> SyntaxElementDescription:
        return SyntaxElementDescription(syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.singular_name,
                                        self._parser.fnap(_SYMBOL_NAME_DESCRIPTION))

    def _cl_arguments(self) -> list:
        return [
            a.Single(a.Multiplicity.OPTIONAL,
                     self._relativity_name),
            a.Single(a.Multiplicity.MANDATORY,
                     self._string_name),

        ]

    def _relativity_options_paragraph(self) -> ParagraphItem:
        return docs.simple_list_with_space_between_elements_and_content([
            docs.list_item(
                self._options_for_directories_in_the(concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO),
                self._options_for_directories_in_the_hds(),
            ),
            docs.list_item(
                self._options_for_directories_in_the(concepts.SANDBOX_CONCEPT_INFO),
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
        ],
            docs.lists.ListType.ITEMIZED_LIST,
        )

    @staticmethod
    def _options_for_directories_in_the(directory_structure: SingularNameAndCrossReferenceId) -> str:
        return 'Options for directories in the ' + formatting.concept_(directory_structure)

    @staticmethod
    def _options_for_directories_in_the_hds() -> list:
        return _options_for_directories_in_the_(REL_HOME_OPTIONS_MAP,
                                                HDS_DIR_DISPLAY_ORDER)

    @staticmethod
    def _options_for_directories_in_the_sds() -> list:
        return _options_for_directories_in_the_(REL_SDS_OPTIONS_MAP,
                                                SDS_DIR_DISPLAY_ORDER)

    def _options_for_current_directory(self) -> list:
        return ([
                    docs.first_row_is_header_table([
                        [docs.text_cell(REL_CWD_INFO.option_name_text)]
                    ])
                ]
                +
                self._parser.fnap(_REL_CD_DESCRIPTION)
                )

    def _options_for_symbol(self) -> list:
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


DOCUMENTATION = _Documentation()


def _options_for_directories_in_the_(rel_opt_2_rel_option_info: dict,
                                     rel_opts_in_display_order: list) -> list:
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


_MAIN_DESCRIPTION_REST = """\
If {PATH_STRING} is an absolute path, then {RELATIVITY_OPTION} must not be given.


If {PATH_STRING} is a relative path, then if {RELATIVITY_OPTION} is ...


  * given
  
    {PATH_STRING} is relative to the directory specified by {RELATIVITY_OPTION}

  * not given
  
    {PATH_STRING} is relative to the default relativity root directory,


The default relativity depends on the instruction,
and also on the argument position of the instruction. 
"""

_STRING_DESCRIPTION_REST = """\
A relative or absolute path, using {posix_syntax}.


It is a value of type {string_type}, and thus uses {string_syntax_element} syntax.
"""

_RELATIVITY_DESCRIPTION_REST = """\
An option that specifies the directory that {PATH_STRING} is relative to.


The available relativities depends on the instruction,
and also on the argument position of the instruction. 


Summary of options:
"""

_REL_CD_DESCRIPTION = """\
This options is needed since many instructions
have a default relativity other than the {cd}.
"""

_REL_SYMBOL_DESCRIPTION = """\
This option is always available.
"""

_SYMBOL_NAME_DESCRIPTION = """\
A {symbol} with type {path_type}.
"""
