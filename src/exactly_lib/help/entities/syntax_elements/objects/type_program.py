from typing import List, Sequence

from exactly_lib.common.help.see_also import SeeAlsoSet
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args, cli_argument_syntax_element_description
from exactly_lib.common.help.with_see_also_set import SyntaxElementDescriptionTree, InvokationVariantHelper
from exactly_lib.definitions import instruction_arguments, formatting, misc_texts
from exactly_lib.definitions.argument_rendering.path_syntax import the_path_of
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import concepts, syntax_elements, actors
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.definitions.test_case.instructions import define_symbol
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help.entities.utils import programs
from exactly_lib.processing import exit_values
from exactly_lib.test_case_utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.test_case_utils.documentation import texts
from exactly_lib.test_case_utils.parse import path_relativities
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
                a.Single(a.Multiplicity.OPTIONAL,
                         string_transformer.STRING_TRANSFORMATION_ARGUMENT),
            ]),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return self._pgm_and_args.syntax_element_definitions + self._global_sed_list()

    def _global_sed_list(self) -> List[SyntaxElementDescription]:
        return [_transformation_sed()]

    def see_also_targets(self) -> List[CrossReferenceId]:
        info_refs = cross_reference_id_list([
            syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT,
            syntax_elements.PROGRAM_ARGUMENT_SYNTAX_ELEMENT,
            syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT,
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

    @property
    def sub_syntax_element_definition_trees(self) -> List[SyntaxElementDescriptionTree]:
        return [
            self._pgm_for_arg_list,
        ]

    def _pgm_for_arg_list_variant(self) -> InvokationVariant:
        return invokation_variant_from_args([
            a.Single(a.Multiplicity.MANDATORY, self._pgm_for_arg_list.element),
            a.Single(a.Multiplicity.ZERO_OR_MORE, syntax_elements.PROGRAM_ARGUMENT_SYNTAX_ELEMENT.argument),
        ],
            _TEXT_PARSER.fnap(_PGM_WITH_ARG_LIST_INVOKATION_VARIANT_DESCRIPTION))


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
            programs.system_program([]),
            self._sym_ref(),
            programs.python_interpreter([]),
        ]

    @staticmethod
    def _exe_file() -> InvokationVariant:
        return invokation_variant_from_args(
            [
                a.Single(a.Multiplicity.MANDATORY,
                         instruction_arguments.PATH_ARGUMENT)
            ],
            rel_path_doc.path_element_relativity_paragraphs(
                path_relativities.REL_OPTIONS_CONFIGURATION,
                _TEXT_PARSER.paras(the_path_of('{executable_file:a}.')),
                _TEXT_PARSER.fnap(_DIFFERENT_RELATIVITIES_FOR_PROGRAM_ACTOR),
            )
        )

    @staticmethod
    def _sym_ref() -> InvokationVariant:
        return invokation_variant_from_args(
            [
                a.Single(a.Multiplicity.MANDATORY,
                         a.Constant(pgm_syntax_elements.SYMBOL_REF_PROGRAM_TOKEN)
                         ),
                a.Single(a.Multiplicity.MANDATORY,
                         syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument
                         ),
            ],
            _TEXT_PARSER.fnap(_SYM_REF_PROGRAM_DESCRIPTION)
        )


def _transformation_description_rest() -> List[ParagraphItem]:
    ret_val = _TEXT_PARSER.fnap(_TRANSFORMATION_DESCRIPTION)
    ret_val += texts.type_expression_has_syntax_of_primitive([
        syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name,
    ])
    return ret_val


def _transformation_sed() -> SyntaxElementDescription:
    return cli_argument_syntax_element_description(
        string_transformer.STRING_TRANSFORMATION_ARGUMENT,
        _transformation_description_rest(),
        [
            invokation_variant_from_args([a.Single(a.Multiplicity.MANDATORY,
                                                   string_transformer.TRANSFORMATION_OPTION)]),
        ]
    )


EXECUTABLE_ARG = a.Named('EXECUTABLE')

_TEXT_PARSER = TextParser({
    'program_type': types.PROGRAM_TYPE_INFO.name,
    'symbol': concepts.SYMBOL_CONCEPT_INFO.name,
    'hds': concepts.HDS_CONCEPT_INFO.name,
    'TRANSFORMATION': string_transformer.STRING_TRANSFORMATION_ARGUMENT.name,
    'define_symbol': instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME,
    'SYMBOL_NAME': formatting.syntax_element_(syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT),
    'ARGUMENT': formatting.syntax_element(syntax_elements.PROGRAM_ARGUMENT_SYNTAX_ELEMENT.singular_name),
    'SHELL_COMMAND_LINE': formatting.syntax_element_(syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT),
    'executable_file': formatting.misc_name_with_formatting(misc_texts.EXECUTABLE_FILE),
    'FAIL': exit_values.EXECUTION__FAIL.exit_identifier,
    'shell_command': formatting.misc_name_with_formatting(misc_texts.SHELL_COMMAND),
    'relativity': formatting.misc_name_with_formatting(misc_texts.RELATIVITY),
    'Note': misc_texts.NOTE_LINE_HEADER,
    'program_actor': formatting.entity_(actors.COMMAND_LINE_ACTOR),
    'actor_concept': formatting.concept_(concepts.ACTOR_CONCEPT_INFO),
})

DOCUMENTATION = _Documentation()

_PGM_AND_ARGS = """\
A program followed by arguments until end of line.
"""

_PGM_WITH_ARG_LIST_INVOKATION_VARIANT_DESCRIPTION = """\
A program with a list of arguments.
"""

_SHELL_COMMAND_INVOKATION_VARIANT_DESCRIPTION = """\
{shell_command:a/u}.


{SHELL_COMMAND_LINE} is the remaining part of the current line.

It is passed as a single string to the operating system's shell.
"""

PGM_WITH_ARG_LIST_DESCRIPTION = """\
An executable program.
"""

_SYM_REF_PROGRAM_DESCRIPTION = """\
Reference to a program that has been defined using the {define_symbol} instruction.


{SYMBOL_NAME} must have been defined as {program_type:a/q}.


Arguments and transformations are appended to existing arguments and transformations
of {SYMBOL_NAME}.
"""

_TRANSFORMATION_DESCRIPTION = """\
Transforms the output from the program.


Depending on the context, either stdout or stderr is transformed.


{Note} Must appear on a separate line.

If not, it will be interpreted as a {ARGUMENT}.
"""

_DIFFERENT_RELATIVITIES_FOR_PROGRAM_ACTOR = """\
{Note} The {relativity:s} are different for the {program_actor} {actor_concept}.
"""
