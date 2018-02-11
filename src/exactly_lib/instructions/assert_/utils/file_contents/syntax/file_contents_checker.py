from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    cli_argument_syntax_element_description
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.entity import syntax_elements, types
from exactly_lib.instructions.assert_.utils.file_contents.syntax import file_contents_matcher as parts_cl_syntax
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser


def file_contents_checker_arguments() -> list:
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
            'file_contents_matcher': syntax_elements.FILE_CONTENTS_MATCHER.argument.name,
        })

    def _cls(self, additional_argument_usages: list) -> str:
        return cl_syntax.cl_syntax_for_args(self.initial_args_of_invokation_variants +
                                            additional_argument_usages)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cls(
                file_contents_checker_arguments()),
                self._tp.fnap(_MAIN_INVOKATION_SYNTAX_DESCRIPTION)),
        ]

    def syntax_element_descriptions_at_top(self) -> list:
        return [self.contents_matcher_help.syntax_element_description()]

    def syntax_element_descriptions_at_bottom(self) -> list:
        transformation = transformation_syntax_element_description(self._checked_file)

        return ([transformation,
                 negation_of_predicate.syntax_element_description()] +
                self.contents_matcher_help.referenced_syntax_element_descriptions()
                )

    def see_also_targets(self) -> list:
        return (
                [types.LINES_TRANSFORMER_TYPE_INFO.cross_reference_target]
                +
                self.contents_matcher_help.see_also_targets()
        )


_MAIN_INVOKATION_SYNTAX_DESCRIPTION = """\
Asserts that the contents of {checked_file} satisfies {file_contents_matcher}.
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
