from typing import List, Sequence

from exactly_lib import program_info
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args, cli_argument_syntax_element_description
from exactly_lib.common.help.with_see_also_set import SyntaxElementDescriptionTree, InvokationVariantHelper
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help_texts import instruction_arguments, formatting
from exactly_lib.help_texts.argument_rendering.path_syntax import the_path_of
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.help_texts.entity import concepts, syntax_elements
from exactly_lib.help_texts.entity import types
from exactly_lib.help_texts.test_case.instructions import define_symbol
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.test_case_utils.parse.rel_opts_configuration import arg_config_with_name
from exactly_lib.test_case_utils.program import syntax_elements as pgm_syntax_elements
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class _Documentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(TypeCategory.LOGIC,
                         syntax_elements.PROGRAM_SYNTAX_ELEMENT)
        self._pgm_and_args = _PgmAndArgs()

    def main_description_rest_paragraphs(self) -> List[ParagraphItem]:
        return []

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY, self._pgm_and_args.element),
                a.Single(a.Multiplicity.OPTIONAL, instruction_arguments.LINES_TRANSFORMATION_ARGUMENT),
            ]),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return self._pgm_and_args.syntax_element_definitions + self._global_sed_list()

    def _global_sed_list(self) -> List[SyntaxElementDescription]:
        return [self._transformation_sed()]

    def _transformation_sed(self) -> SyntaxElementDescription:
        return cli_argument_syntax_element_description(
            instruction_arguments.LINES_TRANSFORMATION_ARGUMENT,
            _TEXT_PARSER.fnap(_TRANSFORMATION_DESCRIPTION),
            [
                invokation_variant_from_args([a.Single(a.Multiplicity.MANDATORY,
                                                       instruction_arguments.TRANSFORMATION_OPTION)]),
            ]
        )

    def see_also_targets(self) -> list:
        info_refs = cross_reference_id_list([
            syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT,
            syntax_elements.LINES_TRANSFORMER_SYNTAX_ELEMENT,
            syntax_elements.STRING_SYNTAX_ELEMENT,
            syntax_elements.LIST_SYNTAX_ELEMENT,
            syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT,
            concepts.SYMBOL_CONCEPT_INFO,
            types.PROGRAM_TYPE_INFO,
        ])
        plain_refs = [
            define_symbol.DEFINE_SYMBOL_INSTRUCTION_CROSS_REFERENCE,
        ]
        return info_refs + plain_refs


class _PgmAndArgs(SyntaxElementDescriptionTree):
    def __init__(self):
        self._pgm_for_arg_list = _ProgramWithArgumentList()
        self._shell_cmd_line = _ShellCommandLine()
        self._arg = _ArgumentDoc()

    @property
    def element(self) -> a.Named:
        return a.Named('PGM-AND-ARGS')

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TEXT_PARSER.fnap(_PGM_AND_ARGS)

    @property
    def invokation_variants(self) -> Sequence[InvokationVariant]:
        return [
            self._pgm_for_arg_list_variant(),
            self._shell_cmd_line.as_invokation_variant,
        ]

    def _pgm_for_arg_list_variant(self) -> InvokationVariant:
        return invokation_variant_from_args([
            a.Single(a.Multiplicity.MANDATORY, self._pgm_for_arg_list.element),
            a.Single(a.Multiplicity.ZERO_OR_MORE, self._arg.element),
        ],
            _TEXT_PARSER.fnap(_PGM_WITH_ARG_LIST_INVOKATION_VARIANT_DESCRIPTION))

    @property
    def sub_syntax_element_definition_trees(self) -> List[SyntaxElementDescriptionTree]:
        return [
            self._pgm_for_arg_list,
            self._arg,
        ]


class _ShellCommandLine(InvokationVariantHelper):
    @property
    def syntax(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant(instruction_names.SHELL_INSTRUCTION_NAME)
                     ),
            a.Single(a.Multiplicity.MANDATORY,
                     syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT.argument)
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TEXT_PARSER.fnap(_SHELL_COMMAND_INVOKATION_VARIANT_DESCRIPTION)


class _ProgramWithArgumentList(SyntaxElementDescriptionTree):
    @property
    def element(self) -> a.Named:
        return a.Named('PGM-FOR-ARG-LIST')

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TEXT_PARSER.fnap(PGM_WITH_ARG_LIST_DESCRIPTION)

    @property
    def invokation_variants(self) -> Sequence[InvokationVariant]:
        return [
            self._exe_file(),
            self._sym_ref(),
            self._python(),
        ]

    @staticmethod
    def _exe_file() -> InvokationVariant:
        return invokation_variant_from_args(
            [
                a.Single(a.Multiplicity.MANDATORY,
                         instruction_arguments.PATH_ARGUMENT)
            ],
            _TEXT_PARSER.fnap(_EXE_FILE_DESCRIPTION)
        )

    @staticmethod
    def _sym_ref() -> InvokationVariant:
        return invokation_variant_from_args(
            [
                a.Single(a.Multiplicity.MANDATORY,
                         a.Constant(instruction_names.SYMBOL_REF_PROGRAM_INSTRUCTION_NAME)
                         ),
                a.Single(a.Multiplicity.MANDATORY,
                         syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument
                         ),
            ],
            _TEXT_PARSER.fnap(_SYM_REF_PROGRAM_DESCRIPTION)
        )

    @staticmethod
    def _python() -> InvokationVariant:
        return invokation_variant_from_args(
            [
                a.Single(a.Multiplicity.MANDATORY,
                         a.Option(pgm_syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME))
            ],
            _TEXT_PARSER.fnap(_PYTHON_EXECUTABLE_DESCRIPTION)
        )


class _ArgumentDoc(SyntaxElementDescriptionTree):
    @property
    def element(self) -> a.Named:
        return pgm_syntax_elements.ARGUMENT_SYNTAX_ELEMENT_NAME

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TEXT_PARSER.fnap(_ARGUMENT_DESCRIPTION)

    @property
    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            self._string(),
            self._list(),
            self._text_until_end_of_line(),
            self._existing_file(),
        ]

    @staticmethod
    def _existing_file():
        return invokation_variant_from_args([
            a.Single(a.Multiplicity.MANDATORY,
                     a.Option(pgm_syntax_elements.EXISTING_FILE_OPTION_NAME)),
            a.Single(a.Multiplicity.MANDATORY,
                     PATH_OF_EXISTING_FILE_OPT_CONFIG.argument)
        ],
            _TEXT_PARSER.fnap(_ARGUMENT__EXISTING_FILE_DESCRIPTION)
        )

    @staticmethod
    def _text_until_end_of_line():
        return invokation_variant_from_args([
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant(pgm_syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER)),
            a.Single(a.Multiplicity.MANDATORY,
                     instruction_arguments.TEXT_UNTIL_END_OF_LINE_ARGUMENT)
        ],
            _TEXT_PARSER.fnap(_ARGUMENT__TEXT_UNTIL_END_OF_LINE_DESCRIPTION)
        )

    @staticmethod
    def _list():
        return invokation_variant_from_args([
            a.Single(a.Multiplicity.MANDATORY, syntax_elements.LIST_SYNTAX_ELEMENT.argument),
        ],
            _TEXT_PARSER.fnap(_ARGUMENT__LIST_DESCRIPTION))

    @staticmethod
    def _string():
        return invokation_variant_from_args([
            a.Single(a.Multiplicity.MANDATORY, syntax_elements.STRING_SYNTAX_ELEMENT.argument),
        ],
            _TEXT_PARSER.fnap(_ARGUMENT__STRING_DESCRIPTION)
        )

    @property
    def sub_syntax_element_definition_trees(self) -> List[SyntaxElementDescriptionTree]:
        return [
            rel_path_doc.path_element_3(PATH_OF_EXISTING_FILE_OPT_CONFIG,
                                        _TEXT_PARSER.paras(the_path_of('an existing file.')))
        ]


PATH_OF_EXISTING_FILE_OPT_CONFIG = arg_config_with_name('PATH-OF-EXISTING-FILE',
                                                        pgm_syntax_elements.REL_OPTION_ARG_CONF)

EXECUTABLE_ARG = a.Named('EXECUTABLE')

_TEXT_PARSER = TextParser({
    'program_name': formatting.program_name(program_info.PROGRAM_NAME),
    'string_type': formatting.keyword(types.STRING_TYPE_INFO.name.singular),
    'string_se': formatting.syntax_element_(syntax_elements.STRING_SYNTAX_ELEMENT),
    'list_type': formatting.keyword(types.LIST_TYPE_INFO.name.singular),
    'list_se': formatting.syntax_element_(syntax_elements.LIST_SYNTAX_ELEMENT),
    'path_type': formatting.keyword(types.PATH_TYPE_INFO.name.singular),
    'path_se': formatting.syntax_element_(syntax_elements.PATH_SYNTAX_ELEMENT),
    'program_type': formatting.keyword(types.PROGRAM_TYPE_INFO.name.singular),
    'symbol': formatting.concept_(concepts.SYMBOL_CONCEPT_INFO),
    'hds': formatting.concept_(concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO),
    'SYMBOL_REFERENCE_SYNTAX_ELEMENT': formatting.syntax_element_(syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT),
    'TRANSFORMATION': instruction_arguments.LINES_TRANSFORMATION_ARGUMENT.name,
    'define_symbol': instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME,
    'TEXT_UNTIL_END_OF_LINE': instruction_arguments.TEXT_UNTIL_END_OF_LINE_ARGUMENT.name,
    'SYMBOL_NAME': formatting.syntax_element_(syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT),
    'THE_PYTHON_INTERPRETER': program_info.PYTHON_INTERPRETER_WHICH_CAN_RUN_THIS_PROGRAM,
    'PATH_OF_EXISTING_FILE': PATH_OF_EXISTING_FILE_OPT_CONFIG.argument_syntax_name,
    'ARGUMENT': formatting.syntax_element(pgm_syntax_elements.ARGUMENT_SYNTAX_ELEMENT_NAME.name),
    'SHELL_COMMAND_LINE': formatting.syntax_element_(syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT),

})

DOCUMENTATION = _Documentation()

_PGM_AND_ARGS = """\
A program followed by arguments until end of line.
"""

_PGM_WITH_ARG_LIST_INVOKATION_VARIANT_DESCRIPTION = """\
A program with a list of arguments.
"""

_SHELL_COMMAND_INVOKATION_VARIANT_DESCRIPTION = """\
A shell command.


{SHELL_COMMAND_LINE} is the remaining part of the current line.

It is passed as a single string to the operating system's shell.
"""

PGM_WITH_ARG_LIST_DESCRIPTION = """\
An executable program.
"""

_EXE_FILE_DESCRIPTION = """\
The path of an executable file.
"""

_SYM_REF_PROGRAM_DESCRIPTION = """\
Reference to a program that has been defined using the {define_symbol} instruction.


{SYMBOL_NAME} must have been defined as a {program_type}.


Arguments and transformations are appended to existing arguments and transformations
of {SYMBOL_NAME}.
"""

_PYTHON_EXECUTABLE_DESCRIPTION = """\
{THE_PYTHON_INTERPRETER}


Since {program_name} is written in Python,
the Python interpreter is guaranteed to be available on the system.
"""

_ARGUMENT_DESCRIPTION = """\
An individual argument, or a list of arguments, in case of an unquoted reference
to a {list_type} {symbol}.


An argument list is an ordinary {list_type} value, with some additional features
for text-until-end-of-line and references to existing files.
"""

_ARGUMENT__STRING_DESCRIPTION = """\
{path_type} values are handled as {string_type} values the usual way -
rendered as an absolute path.
"""

_ARGUMENT__LIST_DESCRIPTION = """\
Elements of referenced lists are appended to the preceding arguments -
argument lists are not nested.


To pass a {list_se} as a single argument to a program,
convert it to a {string_se} by surrounding it with quotes.
(The elements will be separated by a single space.)
"""

_ARGUMENT__TEXT_UNTIL_END_OF_LINE_DESCRIPTION = """\
The remaining part of the current line becomes a single argument.
"""

_ARGUMENT__EXISTING_FILE_DESCRIPTION = """\
A {path_se}, with additional check for existence.


The check for existence is done as soon as possible - during validation
if {PATH_OF_EXISTING_FILE} is absolute or resides inside the {hds}.


Values are rendered as absolute paths.
"""

_TRANSFORMATION_DESCRIPTION = """\
Transforms the output from the program.


Depending on the context, either stdout or stderr is transformed.


Must appear on a separate line.

If not, it will be interpreted as an {ARGUMENT}.
"""
