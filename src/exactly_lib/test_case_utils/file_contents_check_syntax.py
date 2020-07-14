from typing import List

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    cli_argument_syntax_element_description, invokation_variant_from_args
from exactly_lib.definitions import formatting
from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import concepts, syntax_elements, types
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.test_case_utils.documentation import texts
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser


class FileContentsCheckerHelp:
    def __init__(self,
                 instruction_name: str,
                 checked_file: str,
                 initial_args_of_invokation_variants: List[a.ArgumentUsage]):
        self._checked_file = checked_file
        self.instruction_name = instruction_name
        self.initial_args_of_invokation_variants = initial_args_of_invokation_variants
        self._tp = TextParser({
            'checked_file': checked_file,
            'contents_matcher': formatting.syntax_element_(syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT),
            'action_to_check': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
            'program_type': types.PROGRAM_TYPE_INFO.name,
            'The_program_type_must_terminate': texts.THE_PROGRAM_TYPE_MUST_TERMINATE_SENTENCE,
        })

    def invokation_variants__file(self, actual_file: a.Named) -> List[InvokationVariant]:
        actual_file_arg = a.Single(a.Multiplicity.MANDATORY,
                                   actual_file)
        return [
            invokation_variant_from_args(
                [actual_file_arg] + file_contents_checker_arguments__non_program(),
                self._tp.fnap(_MAIN_INVOKATION__FILE__SYNTAX_DESCRIPTION)),
        ]

    def invokation_variants__stdout_err(self, program_option: a.OptionName) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args(
                file_contents_checker_arguments__non_program(),
                self._tp.fnap(_MAIN_INVOKATION__STDOUT_ERR_ACTION_TO_CHECK__SYNTAX_DESCRIPTION)
            ),
            invokation_variant_from_args(
                file_contents_checker_arguments__program(program_option),
                self._tp.fnap(_MAIN_INVOKATION__STDOUT_ERR_PROGRAM__SYNTAX_DESCRIPTION)
            ),
        ]

    @staticmethod
    def see_also_targets__file() -> List[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.PATH_SYNTAX_ELEMENT,
            syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT,
        ])

    @staticmethod
    def see_also_targets__std_out_err() -> List[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT,
            syntax_elements.PROGRAM_SYNTAX_ELEMENT,
            concepts.ACTION_TO_CHECK_CONCEPT_INFO,
        ])


def file_contents_checker_arguments__non_program() -> List[a.ArgumentUsage]:
    file_contents_arg = a.Single(a.Multiplicity.MANDATORY,
                                 syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.argument)

    return [
        file_contents_arg,
    ]


def file_contents_checker_arguments__program(program_option: a.OptionName) -> List[a.ArgumentUsage]:
    file_contents_arg = a.Single(a.Multiplicity.MANDATORY,
                                 syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.argument)

    program_output_option = a.Single(a.Multiplicity.MANDATORY,
                                     a.Option(program_option))

    program_arg = a.Single(a.Multiplicity.MANDATORY,
                           syntax_elements.PROGRAM_SYNTAX_ELEMENT.argument)
    return [
        program_output_option,
        program_arg,
        file_contents_arg,
    ]


_MAIN_INVOKATION__FILE__SYNTAX_DESCRIPTION = """\
Asserts that the contents of {checked_file} satisfies {contents_matcher}.
"""

_MAIN_INVOKATION__STDOUT_ERR_ACTION_TO_CHECK__SYNTAX_DESCRIPTION = """\
Asserts that {checked_file} from the {action_to_check} satisfies {contents_matcher}.
"""

_MAIN_INVOKATION__STDOUT_ERR_PROGRAM__SYNTAX_DESCRIPTION = """\
Asserts that {checked_file} from {program_type:a/q} satisfies {contents_matcher}.


{contents_matcher} must appear on a separate line.


{The_program_type_must_terminate}
"""


def transformation_syntax_element_description(the_tested_file: str) -> SyntaxElementDescription:
    text_parser = TextParser({
        'the_tested_file': the_tested_file,
        'transformer': syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name,
    })
    return cli_argument_syntax_element_description(
        string_transformer.STRING_TRANSFORMATION_ARGUMENT,
        text_parser.fnap(_TRANSFORMATION_DESCRIPTION),
        [
            InvokationVariant(cl_syntax.arg_syntax(
                string_transformer.TRANSFORMATION_OPTION)),
        ]
    )


_TRANSFORMATION_DESCRIPTION = """\
Makes the assertion apply to the result of applying {transformer} to
the contents of {the_tested_file},
instead of to its original contents.
"""
