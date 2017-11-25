from exactly_lib import program_info
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.formatting import InstructionName
from exactly_lib.instructions.assert_.utils.expression import parse as parse_expr
from exactly_lib.instructions.assert_.utils.file_contents.parts import cl_syntax as parts_cl_syntax
from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.test_case_utils.lines_transformer import parse_lines_transformer
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser


class FileContentsHelpParts:
    def __init__(self,
                 instruction_name: str,
                 checked_file: str,
                 initial_args_of_invokation_variants: list):
        self.file_contents_assertion_help = parts_cl_syntax.FileContentsAssertionHelp(checked_file)
        self.instruction_name = instruction_name
        self.initial_args_of_invokation_variants = initial_args_of_invokation_variants
        self.expected_file_arg = a.Named('EXPECTED-PATH')
        format_map = {
            'instruction_name': InstructionName(instruction_name),
            'checked_file': checked_file,
            'expected_file_arg': self.expected_file_arg.name,
            'not_option': instruction_arguments.NEGATION_ARGUMENT_STR,
            'program_name': program_info.PROGRAM_NAME,
            'home_act_env_var': environment_variables.ENV_VAR_HOME_ACT,
            'home_case_env_var': environment_variables.ENV_VAR_HOME_CASE,
            'transformation': instruction_arguments.LINES_TRANSFORMATION_ARGUMENT.name,
            'any': instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
            'every': instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
            'file_contents_assertion': parts_cl_syntax.FILE_CONTENTS_ASSERTION.name,
        }
        self._parser = TextParser(format_map)

    def _cls(self, additional_argument_usages: list) -> str:
        return cl_syntax.cl_syntax_for_args(self.initial_args_of_invokation_variants + additional_argument_usages)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cls(parts_cl_syntax.file_contents_assertion_arguments()),
                              self._paragraphs(_MAIN_INVOKATION_SYNTAX_DESCRIPTION)),
        ]

    def syntax_element_descriptions_at_top(self) -> list:
        return [negation_of_predicate.syntax_element_description(),
                self.file_contents_assertion_help.file_contents_assertion_sed()]

    def syntax_element_descriptions_at_bottom(self) -> list:
        transformation = parse_lines_transformer.selection_syntax_element_description()

        return ([transformation] +
                self.file_contents_assertion_help.used_syntax_element_descriptions() +
                parse_expr.syntax_element_descriptions(parse_expr.NON_NEGATIVE_INTEGER_ARGUMENT_DESCRIPTION)
                )

    def see_also_targets(self) -> list:
        return self.file_contents_assertion_help.see_also_targets()

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self._parser.fnap(s, extra)


_MAIN_INVOKATION_SYNTAX_DESCRIPTION = """\
Asserts that the contents of {checked_file} satisfies {file_contents_assertion}.
"""
