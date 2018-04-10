from typing import List

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    cli_argument_syntax_element_description, invokation_variant_from_args
from exactly_lib.definitions import formatting
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.definitions.entity import concepts, syntax_elements, types
from exactly_lib.instructions.assert_.utils.file_contents.syntax import file_contents_matcher as parts_cl_syntax
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser


class FileContentsCheckerHelp:
    def __init__(self,
                 instruction_name: str,
                 checked_file: str,
                 initial_args_of_invokation_variants: list):
        self._checked_file = checked_file
        self.contents_matcher_help = parts_cl_syntax.FileContentsMatcherHelp()
        self.instruction_name = instruction_name
        self.initial_args_of_invokation_variants = initial_args_of_invokation_variants
        self._tp = TextParser({
            'checked_file': checked_file,
            'file_contents_matcher': formatting.syntax_element_(syntax_elements.FILE_CONTENTS_MATCHER),
            'action_to_check': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
            'program_type': formatting.entity_(types.PROGRAM_TYPE_INFO),
        })

    def _cls(self, additional_argument_usages: list) -> str:
        return cl_syntax.cl_syntax_for_args(self.initial_args_of_invokation_variants +
                                            additional_argument_usages)

    def invokation_variants__file(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args(
                file_contents_checker_arguments__non_program(),
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

    def syntax_element_descriptions_at_top(self) -> list:
        return []

    def syntax_element_descriptions_at_bottom(self) -> list:
        transformation = transformation_syntax_element_description(self._checked_file)

        return ([transformation,
                 negation_of_predicate.syntax_element_description()]
        )

    def see_also_targets__file(self) -> list:
        return [
            syntax_elements.FILE_CONTENTS_MATCHER.cross_reference_target,
            syntax_elements.LINES_TRANSFORMER_SYNTAX_ELEMENT.cross_reference_target,
        ]

    def see_also_targets__stdout_err(self) -> list:
        return [
            syntax_elements.FILE_CONTENTS_MATCHER.cross_reference_target,
            syntax_elements.PROGRAM_SYNTAX_ELEMENT.cross_reference_target,
            syntax_elements.LINES_TRANSFORMER_SYNTAX_ELEMENT.cross_reference_target,
            concepts.ACTION_TO_CHECK_CONCEPT_INFO.cross_reference_target,
        ]


def file_contents_checker_arguments__non_program() -> List[a.ArgumentUsage]:
    file_contents_arg = a.Single(a.Multiplicity.MANDATORY,
                                 syntax_elements.FILE_CONTENTS_MATCHER.argument)

    optional_not_arg = negation_of_predicate.optional_negation_argument_usage()

    optional_transformation_option = a.Single(a.Multiplicity.OPTIONAL,
                                              instruction_arguments.LINES_TRANSFORMATION_ARGUMENT)
    return [
        optional_transformation_option,
        optional_not_arg,
        file_contents_arg,
    ]


def file_contents_checker_arguments__program(program_option: a.OptionName) -> List[a.ArgumentUsage]:
    file_contents_arg = a.Single(a.Multiplicity.MANDATORY,
                                 syntax_elements.FILE_CONTENTS_MATCHER.argument)

    optional_not_arg = negation_of_predicate.optional_negation_argument_usage()

    program_output_option = a.Single(a.Multiplicity.MANDATORY,
                                     a.Option(program_option))

    program_arg = a.Single(a.Multiplicity.MANDATORY,
                           syntax_elements.PROGRAM_SYNTAX_ELEMENT.argument)
    return [
        program_output_option,
        program_arg,
        optional_not_arg,
        file_contents_arg,
    ]


_MAIN_INVOKATION__FILE__SYNTAX_DESCRIPTION = """\
Asserts that the contents of {checked_file} satisfies {file_contents_matcher}.
"""

_MAIN_INVOKATION__STDOUT_ERR_ACTION_TO_CHECK__SYNTAX_DESCRIPTION = """\
Asserts that {checked_file} from the {action_to_check} satisfies {file_contents_matcher}.
"""

_MAIN_INVOKATION__STDOUT_ERR_PROGRAM__SYNTAX_DESCRIPTION = """\
Asserts that {checked_file} from a {program_type} satisfies {file_contents_matcher}.
"""


def transformation_syntax_element_description(the_tested_file: str) -> SyntaxElementDescription:
    text_parser = TextParser({
        'the_tested_file': the_tested_file,
        'transformer': syntax_elements.LINES_TRANSFORMER_SYNTAX_ELEMENT.singular_name,
    })
    return cli_argument_syntax_element_description(
        instruction_arguments.LINES_TRANSFORMATION_ARGUMENT,
        text_parser.fnap(_TRANSFORMATION_DESCRIPTION),
        [
            InvokationVariant(cl_syntax.arg_syntax(instruction_arguments.TRANSFORMATION_OPTION)),
        ]
    )


_TRANSFORMATION_DESCRIPTION = """\
Makes the assertion apply to the result of applying {transformer} to
the contents of {the_tested_file},
instead of to its original contents.
"""
