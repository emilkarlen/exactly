from exactly_lib import program_info
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.help.syntax_elements import here_document
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.names.formatting import InstructionName
from exactly_lib.instructions.assert_.utils.expression import parse as parse_expr
from exactly_lib.instructions.assert_.utils.file_contents.parse_file_contents_assertion_part import \
    EXPECTED_FILE_REL_OPT_ARG_CONFIG
from exactly_lib.instructions.assert_.utils.file_contents.parts import cl_syntax as parts_cl_syntax
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.test_case_utils.lines_transformer import parse_lines_transformer
from exactly_lib.util.cli_syntax.elements import argument as a


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

        mandatory_path = path_syntax.path_or_symbol_reference(a.Multiplicity.MANDATORY,
                                                              instruction_arguments.PATH_ARGUMENT)

        relativity_of_expected_arg = a.Named('RELATIVITY-OF-EXPECTED-PATH')
        optional_relativity_of_expected = a.Single(a.Multiplicity.OPTIONAL,
                                                   relativity_of_expected_arg)
        return ([
                    transformation,
                    SyntaxElementDescription(self.expected_file_arg.name,
                                             self._paragraphs("The file that contains the expected contents."),
                                             [InvokationVariant(cl_syntax.cl_syntax_for_args(
                                                 [optional_relativity_of_expected,
                                                  mandatory_path]),
                                                 rel_opts.default_relativity_for_rel_opt_type(
                                                     EXPECTED_FILE_REL_OPT_ARG_CONFIG.argument_syntax_name,
                                                     EXPECTED_FILE_REL_OPT_ARG_CONFIG.options.default_option)
                                             )]
                                             ),
                ] +
                rel_opts.relativity_syntax_element_descriptions(
                    instruction_arguments.PATH_ARGUMENT,
                    EXPECTED_FILE_REL_OPT_ARG_CONFIG.options,
                    relativity_of_expected_arg) +
                [
                    SyntaxElementDescription(instruction_arguments.REG_EX.name,
                                             self._parser.fnap('A Python regular expression.')),
                    here_document.here_document_syntax_element_description(self.instruction_name,
                                                                           instruction_arguments.HERE_DOCUMENT),
                ] +
                parse_expr.syntax_element_descriptions(parse_expr.NON_NEGATIVE_INTEGER_ARGUMENT_DESCRIPTION)
                )

    def see_also_items(self) -> list:
        return self.file_contents_assertion_help.see_also_items()

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self._parser.fnap(s, extra)


_MAIN_INVOKATION_SYNTAX_DESCRIPTION = """\
Asserts that the contents of {checked_file} satisfies {file_contents_assertion}.
"""
