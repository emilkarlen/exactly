from typing import List

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args, cli_argument_syntax_element_description
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help_texts import instruction_arguments, formatting
from exactly_lib.help_texts.argument_rendering.path_syntax import the_path_of
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.help_texts.entity import concepts, syntax_elements
from exactly_lib.help_texts.entity import types
from exactly_lib.help_texts.test_case.instructions import define_symbol
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.program_info import PYTHON_INTERPRETER_WHICH_CAN_RUN_THIS_PROGRAM
from exactly_lib.test_case_utils.program import syntax_elements as pgm_syntax_elements
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class _Documentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(TypeCategory.LOGIC,
                         syntax_elements.PROGRAM_SYNTAX_ELEMENT)

    def main_description_rest_paragraphs(self) -> List[ParagraphItem]:
        return []

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            self._executable_file_variant(),
            self._shell_command_variant(),
            self._program_symbol_reference_variant(),
        ]

    def _program_symbol_reference_variant(self):
        return self._with_optional_transformation([
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant(instruction_names.SYMBOL_REF_PROGRAM_INSTRUCTION_NAME)
                     ),
            a.Single(a.Multiplicity.MANDATORY,
                     PROGRAM_SYMBOL_NAME_ARG
                     ),
            a.Single(a.Multiplicity.ZERO_OR_MORE,
                     GENERIC_ARG
                     ),
        ], _SYMBOL_REFERENCE_TO_PROGRAM_DESCRIPTION)

    def _shell_command_variant(self):
        return self._with_optional_transformation([
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant(instruction_names.SHELL_INSTRUCTION_NAME)
                     ),
            a.Single(a.Multiplicity.MANDATORY,
                     instruction_arguments.COMMAND_ARGUMENT)
        ],
            _SHELL_COMMAND_VARIANT_DESCRIPTION)

    def _executable_file_variant(self):
        return self._with_optional_transformation([
            a.Single(a.Multiplicity.MANDATORY,
                     EXECUTABLE_FILE_PROGRAM_ARG
                     )],
            _EXECUTABLE_FILE_PROGRAM_VARIANT_DESCRIPTION
        )

    def _with_optional_transformation(self,
                                      before_trans: List[a.ArgumentUsage],
                                      description_rest: str) -> InvokationVariant:
        return invokation_variant_from_args(
            before_trans +
            [
                a.Single(a.Multiplicity.OPTIONAL,
                         instruction_arguments.LINES_TRANSFORMATION_ARGUMENT)],
            _TEXT_PARSER.fnap(description_rest)

        )

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        exe_file_doc = _ExecutableFileDoc()
        exe_file_pgm_doc = _ProgramFromExecutableFileDoc()
        arg_doc = _ArgumentDoc()
        return [
            exe_file_pgm_doc.sed(),
            exe_file_doc.sed(),
            rel_path_doc.path_element_2(pgm_syntax_elements.REL_OPTION_ARG_CONF,
                                        _TEXT_PARSER.paras(the_path_of('an existing file.'))),
            self._transformation_sed(),
            self._symbol_reference_sed(),
            arg_doc.sed(),

        ]

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
            concepts.SYMBOL_CONCEPT_INFO,
            types.PROGRAM_TYPE_INFO,
        ])
        plain_refs = [
            define_symbol.DEFINE_SYMBOL_INSTRUCTION_CROSS_REFERENCE,
        ]
        return info_refs + plain_refs

    def _symbol_reference_sed(self) -> SyntaxElementDescription:
        return SyntaxElementDescription(syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.argument.name,
                                        _TEXT_PARSER.fnap(_SYMBOL_REFERENCE_DESCRIPTION))


class _ProgramFromExecutableFileDoc:
    def __init__(self):
        self.relativity_arg_path = instruction_arguments.PATH_ARGUMENT
        self.mandatory_path = a.Single(a.Multiplicity.MANDATORY,
                                       instruction_arguments.PATH_ARGUMENT)
        self.optional_relativity = instruction_arguments.OPTIONAL_RELATIVITY_ARGUMENT_USAGE
        self.mandatory_executable = a.Single(a.Multiplicity.MANDATORY,
                                             EXECUTABLE_ARG)
        self.zero_or_more_generic_args = a.Single(a.Multiplicity.ZERO_OR_MORE,
                                                  GENERIC_ARG)
        self._single_line_description = _PROGRAM_FROM_EXECUTABLE_FILE_SINGLE_LINE_DESCRIPTION

    def sed(self) -> SyntaxElementDescription:
        return SyntaxElementDescription(EXECUTABLE_FILE_PROGRAM_ARG.name,
                                        _TEXT_PARSER.fnap(_EXECUTABLE_FILE_PROGRAM_DESCRIPTION),
                                        self.invokation_variants())

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.OPTIONAL, a.Constant(pgm_syntax_elements.OPTIONS_SEPARATOR_ARGUMENT)),
                self.zero_or_more_generic_args],
                _TEXT_PARSER.fnap(_EXECUTABLE_FILE)),

            invokation_variant_from_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.MANDATORY, a.Option(pgm_syntax_elements.EXISTING_FILE_OPTION_NAME)),
                self.mandatory_path,
                self.zero_or_more_generic_args],
                _TEXT_PARSER.fnap(_SOURCE_FILE)),

            invokation_variant_from_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.MANDATORY,
                         a.Constant(pgm_syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER)),
                a.Single(a.Multiplicity.MANDATORY, a.Named(pgm_syntax_elements.SOURCE_SYNTAX_ELEMENT_NAME))],
                _TEXT_PARSER.fnap(_SOURCE_STRING)),
        ]


class _ExecutableFileDoc:
    def __init__(self):
        self.relativity_arg_path = instruction_arguments.PATH_ARGUMENT
        self.mandatory_path = a.Single(a.Multiplicity.MANDATORY,
                                       instruction_arguments.PATH_ARGUMENT)
        self.optional_relativity = instruction_arguments.OPTIONAL_RELATIVITY_ARGUMENT_USAGE
        self.mandatory_executable = a.Single(a.Multiplicity.MANDATORY,
                                             EXECUTABLE_ARG)
        self.zero_or_more_generic_args = a.Single(a.Multiplicity.ZERO_OR_MORE,
                                                  GENERIC_ARG)

    def sed(self) -> SyntaxElementDescription:
        executable_path_arguments = [self.mandatory_path]
        left_parenthesis = a.Single(a.Multiplicity.MANDATORY, a.Constant('('))
        right_parenthesis = a.Single(a.Multiplicity.MANDATORY, a.Constant(')'))
        executable_in_parenthesis_arguments = ([left_parenthesis] +
                                               executable_path_arguments +
                                               [self.zero_or_more_generic_args,
                                                right_parenthesis])
        python_interpreter_argument = a.Single(a.Multiplicity.MANDATORY,
                                               a.Option(pgm_syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME))
        python_interpreter_arguments = [python_interpreter_argument]
        python_interpreter_in_parenthesis_arguments = [left_parenthesis,
                                                       python_interpreter_argument,
                                                       self.zero_or_more_generic_args,
                                                       right_parenthesis]

        return SyntaxElementDescription(
            EXECUTABLE_ARG.name,
            _TEXT_PARSER.fnap(_EXECUTABLE_DESCRIPTION),
            [
                invokation_variant_from_args(executable_path_arguments,
                                             _TEXT_PARSER.fnap('An executable file.')),
                invokation_variant_from_args(executable_in_parenthesis_arguments,
                                             _TEXT_PARSER.fnap('An executable file with arguments. '
                                                               '(Must be inside parentheses.)')),
                invokation_variant_from_args(python_interpreter_arguments,
                                             _TEXT_PARSER.fnap(PYTHON_INTERPRETER_WHICH_CAN_RUN_THIS_PROGRAM)),
                invokation_variant_from_args(python_interpreter_in_parenthesis_arguments,
                                             _TEXT_PARSER.fnap(PYTHON_INTERPRETER_WHICH_CAN_RUN_THIS_PROGRAM +
                                                               ' (Must be inside parentheses.)')),
            ])

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.OPTIONAL, a.Constant(pgm_syntax_elements.OPTIONS_SEPARATOR_ARGUMENT)),
                self.zero_or_more_generic_args],
                _TEXT_PARSER.fnap(_EXECUTABLE_FILE)),

            invokation_variant_from_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.MANDATORY, a.Constant(pgm_syntax_elements.EXISTING_FILE_OPTION_NAME)),
                self.mandatory_path,
                self.zero_or_more_generic_args],
                _TEXT_PARSER.fnap(_SOURCE_FILE)),

            invokation_variant_from_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.MANDATORY,
                         a.Constant(pgm_syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER)),
                a.Single(a.Multiplicity.MANDATORY, a.Named(pgm_syntax_elements.SOURCE_SYNTAX_ELEMENT_NAME))],
                _TEXT_PARSER.fnap(_SOURCE_STRING)),
        ]


class _ArgumentDoc:
    def sed(self) -> SyntaxElementDescription:
        return SyntaxElementDescription(
            pgm_syntax_elements.ARGUMENT_SYNTAX_ELEMENT_NAME.name,
            _TEXT_PARSER.fnap(_ARGUMENT_DESCRIPTION),
            self.invokation_variants())

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY, syntax_elements.STRING_SYNTAX_ELEMENT.argument),
            ]),

            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY, syntax_elements.LIST_SYNTAX_ELEMENT.argument),
            ]),

            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY,
                         a.Constant(pgm_syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER)),
                a.Single(a.Multiplicity.MANDATORY,
                         instruction_arguments.LITERAL_TEXT_UNTIL_END_OF_LINE_ARGUMENT)
            ]),

            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY,
                         a.Option(pgm_syntax_elements.EXISTING_FILE_OPTION_NAME)),
                a.Single(a.Multiplicity.MANDATORY,
                         syntax_elements.PATH_SYNTAX_ELEMENT.argument)
            ]),
        ]


PROGRAM_AND_ARGS_LINE_ARG = a.Named('PROGRAM-AND-ARGUMENTS-LINE')

EXECUTABLE_FILE_PROGRAM_ARG = a.Named('EXECUTABLE-FILE-PROGRAM')

EXECUTABLE_ARG = a.Named('EXECUTABLE')

GENERIC_ARG = a.Named('ARGUMENT')

PROGRAM_SYMBOL_NAME_ARG = a.Named('PROGRAM-SYMBOL-NAME')

_TEXT_PARSER = TextParser({
    'EXECUTABLE': EXECUTABLE_ARG.name,
    'EXECUTABLE_FILE': EXECUTABLE_FILE_PROGRAM_ARG.name,
    'shell_syntax_concept': formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
    'string_type': formatting.keyword(types.STRING_TYPE_INFO.name.singular),
    'list_type': formatting.keyword(types.LIST_TYPE_INFO.name.singular),
    'path_type': formatting.keyword(types.PATH_TYPE_INFO.name.singular),
    'symbol': formatting.concept_(concepts.SYMBOL_CONCEPT_INFO),
    'SYMBOL_REFERENCE_SYNTAX_ELEMENT': syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.singular_name,
    'TRANSFORMATION': instruction_arguments.LINES_TRANSFORMATION_ARGUMENT.name,
    'PROGRAM_SYMBOL_NAME': PROGRAM_SYMBOL_NAME_ARG.name,
    'define_symbol': instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME,

})

DOCUMENTATION = _Documentation()

_PROGRAM_FROM_EXECUTABLE_FILE_SINGLE_LINE_DESCRIPTION = 'A program with an {EXECUTABLE_FILE}'

_EXECUTABLE_FILE_PROGRAM_VARIANT_DESCRIPTION = """\
An executable file with arguments.


All elements on the current line are considered arguments.


If given, {TRANSFORMATION} must appear on a separate line.
"""

_SHELL_COMMAND_VARIANT_DESCRIPTION = """\
A single line that is passed as a single string to the operating system's shell.


If given, {TRANSFORMATION} must appear on a separate line.
"""

_SYMBOL_REFERENCE_TO_PROGRAM_DESCRIPTION = """\
Reference to a program that has been defined using the {define_symbol} instruction.


Arguments continue until end of line, and are appended to any existing arguments of
{PROGRAM_SYMBOL_NAME}.


If given, {TRANSFORMATION} must appear on a separate line.
It is appended to any existing transformations of {PROGRAM_SYMBOL_NAME}.

"""

_TRANSFORMATION_DESCRIPTION = """\
Transforms the output from the program.


Depending on the context, either stdout or stderr is transformed.
"""

_SYMBOL_REFERENCE_DESCRIPTION = """\
A reference to a {symbol} defined as either {string_type}, {list_type} or {path_type}.
"""

PROGRAM_AND_ARGS_LINE_DESCRIPTION = """
A line with a program and arguments, except for transformation.
"""

_EXECUTABLE_FILE_PROGRAM_DESCRIPTION = """\
Specifies a program that is an existing executable file, and arguments.
"""

_EXECUTABLE_DESCRIPTION = """\
Specifies a program by giving the path to an executable file,
and optionally also arguments to the executable.


Elements uses {shell_syntax_concept}.
"""

_ARGUMENT_DESCRIPTION = """\
TODO
"""

_EXECUTABLE_FILE = """\
Executes the given executable with the given command line arguments.

The arguments are splitted according to {shell_syntax_concept}.
"""

_SOURCE_FILE = """\
Interprets the given source file using {EXECUTABLE}.

Arguments are splitted according to {shell_syntax_concept}.
"""

_SOURCE_STRING = """\
Interprets the given source string using {EXECUTABLE}.

SOURCE is taken literary, and is given as a single argument to {EXECUTABLE}.
"""
