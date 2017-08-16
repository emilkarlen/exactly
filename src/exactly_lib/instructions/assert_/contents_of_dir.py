import pathlib

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.test_case.instructions.assign_symbol import ASSIGN_SYMBOL_INSTRUCTION_CROSS_REFERENCE
from exactly_lib.instructions.assert_.utils import negation_of_assertion
from exactly_lib.instructions.assert_.utils import parse_dir_contents_selector
from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions as pfh_ex_method
from exactly_lib.instructions.assert_.utils.expression import comparison_structures
from exactly_lib.instructions.assert_.utils.expression import parse as expression_parse
from exactly_lib.instructions.assert_.utils.expression.parse import IntegerComparisonOperatorAndRightOperand, \
    ARGUMENTS_FOR_COMPARISON_WITH_OPTIONAL_OPERATOR
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_ARGUMENT, \
    EMPTY_ARGUMENT_CONSTANT
from exactly_lib.instructions.utils import return_svh_via_exceptions
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.err_msg import diff_msg
from exactly_lib.instructions.utils.err_msg.path_description import path_value_description
from exactly_lib.instructions.utils.err_msg.property_description import PropertyDescriptor
from exactly_lib.instructions.utils.expectation_type import ExpectationType
from exactly_lib.instructions.utils.parse.token_stream_parse import new_token_parser
from exactly_lib.instructions.utils.parse.token_stream_parse_prime import TokenParserPrime
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import pfh, svh
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils import file_ref_check
from exactly_lib.test_case_utils.parse import rel_opts_configuration
from exactly_lib.util import dir_contents_selection
from exactly_lib.util.cli_syntax.elements import argument as a


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  TheInstructionDocumentation(instruction_name))


_NUM_FILES_PROPERTY_NAME = 'number of files in dir'

_EMPTINESS_PROPERTY_NAME = 'contents of dir'

NEGATION_OPERATOR = negation_of_assertion.NEGATION_ARGUMENT_STR

SELECTION_OPTION = parse_dir_contents_selector.SELECTION_OPTION

NUM_FILES_CHECK_ARGUMENT = 'num-files'

NUM_FILES_ARGUMENT_CONSTANT = a.Constant(NUM_FILES_CHECK_ARGUMENT)

_CHECKERS = [
    NUM_FILES_CHECK_ARGUMENT,
    EMPTINESS_CHECK_ARGUMENT,
]


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        super().__init__(name, {
            'checked_file': _PATH_ARGUMENT.name,
            'selection': parse_dir_contents_selector.SELECTION.name,
        })
        self.actual_file = a.Single(a.Multiplicity.MANDATORY,
                                    _PATH_ARGUMENT)
        self.relativity_of_actual_arg = a.Named('RELATIVITY')
        self.actual_file_relativity = a.Single(a.Multiplicity.OPTIONAL,
                                               self.relativity_of_actual_arg)

    def single_line_description(self) -> str:
        return _SINGLE_LINE_DESCRIPTION

    def main_description_rest(self) -> list:
        return self._paragraphs(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> list:
        negation_argument = negation_of_assertion.optional_negation_argument_usage()
        selection_arg = a.Single(a.Multiplicity.OPTIONAL,
                                 parse_dir_contents_selector.SELECTION)
        mandatory_empty_arg = a.Single(a.Multiplicity.MANDATORY,
                                       EMPTY_ARGUMENT_CONSTANT)

        mandatory_num_files_arg = a.Single(a.Multiplicity.MANDATORY,
                                           NUM_FILES_ARGUMENT_CONSTANT)

        arguments_for_empty_check = [self.actual_file,
                                     selection_arg,
                                     negation_argument,
                                     mandatory_empty_arg]

        arguments_for_num_files_check = [self.actual_file,
                                         selection_arg,
                                         negation_argument,
                                         mandatory_num_files_arg,
                                         ] + ARGUMENTS_FOR_COMPARISON_WITH_OPTIONAL_OPERATOR

        return [
            InvokationVariant(self._cl_syntax_for_args(arguments_for_empty_check),
                              self._paragraphs(_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY)),

            InvokationVariant(self._cl_syntax_for_args(arguments_for_num_files_check),
                              self._paragraphs(_CHECKS_THAT_DIRECTORY_CONTAINS_SPECIFIED_NUMBER_OF_FILES)),
        ]

    def syntax_element_descriptions(self) -> list:
        negation = negation_of_assertion.syntax_element_description(_ADDITIONAL_TEXT_OF_NEGATION_SED)

        selection = parse_dir_contents_selector.selection_syntax_element_description()

        selector = parse_dir_contents_selector.selector_syntax_element_description()

        mandatory_actual_path = path_syntax.path_or_symbol_reference(a.Multiplicity.MANDATORY,
                                                                     path_syntax.PATH_ARGUMENT)
        actual_file_arg_sed = SyntaxElementDescription(
            _PATH_ARGUMENT.name,
            self._paragraphs(
                _PATH_SYNTAX_ELEMENT_DESCRIPTION_TEXT),
            [InvokationVariant(
                self._cl_syntax_for_args(
                    [self.actual_file_relativity,
                     mandatory_actual_path]
                ),
                rel_opts.default_relativity_for_rel_opt_type(
                    path_syntax.PATH_ARGUMENT.name,
                    ACTUAL_RELATIVITY_CONFIGURATION.options.default_option))]
        )

        relativity_of_actual_file_sed = rel_opts.relativity_syntax_element_description(
            path_syntax.PATH_ARGUMENT,
            ACTUAL_RELATIVITY_CONFIGURATION.options,
            self.relativity_of_actual_arg)

        return ([negation,
                 selection,
                 selector] +
                expression_parse.syntax_element_descriptions() +
                [actual_file_arg_sed,
                 relativity_of_actual_file_sed,
                 ])

    def _see_also_cross_refs(self) -> list:
        concepts = rel_path_doc.see_also_concepts(ACTUAL_RELATIVITY_CONFIGURATION.options)
        refs = rel_path_doc.cross_refs_for_concepts(concepts)
        refs.append(ASSIGN_SYMBOL_INSTRUCTION_CROSS_REFERENCE)
        return refs

    def _cls(self, additional_argument_usages: list) -> str:
        return self._cl_syntax_for_args([self.actual_file] + additional_argument_usages)


class Parser(InstructionParserThatConsumesCurrentLine):
    def __init__(self):
        self.format_map = {
            'PATH': _PATH_ARGUMENT.name,
        }
        self.missing_check_description = 'Missing arguments for check (one of {})'.format(
            ', '.join(map(lambda x: '"' + x + '"', _CHECKERS))
        )

    def _parse(self, rest_of_line: str) -> AssertPhaseInstruction:
        tokens = new_token_parser(rest_of_line,
                                  self.format_map)
        path_to_check = tokens.consume_file_ref(ACTUAL_RELATIVITY_CONFIGURATION)
        file_selection = parse_dir_contents_selector.parse_optional_selection_option(tokens)
        expectation_type = tokens.consume_optional_negation_operator()
        instructions_parser = _CheckInstructionParser(_Settings(expectation_type,
                                                                path_to_check,
                                                                file_selection))

        command_parsers = {
            NUM_FILES_CHECK_ARGUMENT: instructions_parser.parse_num_files_check,
            EMPTINESS_CHECK_ARGUMENT: instructions_parser.parse_empty_check,
        }
        instruction = tokens.parse_mandatory_command(command_parsers,
                                                     self.missing_check_description)
        tokens.report_superfluous_arguments_if_not_at_eol()
        return instruction


class _Settings:
    def __init__(self,
                 expectation_type: ExpectationType,
                 path_to_check: FileRefResolver,
                 file_selector: dir_contents_selection.Selectors):
        self.expectation_type = expectation_type
        self.path_to_check = path_to_check
        self.file_selector = file_selector


class _CheckInstructionParser:
    def __init__(self, settings: _Settings):
        self.settings = settings

    def parse_empty_check(self, parser: TokenParserPrime) -> AssertPhaseInstruction:
        return _InstructionForEmptiness(self.settings)

    def parse_num_files_check(self, parser: TokenParserPrime) -> AssertPhaseInstruction:
        cmp_op_and_rhs = expression_parse.parse_integer_comparison_operator_and_rhs(
            parser,
            expression_parse.validator_for_non_negative)

        return _InstructionForNumFiles(self.settings, cmp_op_and_rhs)


class _InstructionBase(AssertPhaseInstruction):
    def __init__(self, path_to_check: FileRefResolver):
        self.path_to_check = path_to_check

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return pfh_ex_method.translate_pfh_exception_to_pfh(self.__main_that_reports_result_via_exceptions,
                                                            environment)

    def _property_descriptor(self, property_name: str) -> PropertyDescriptor:
        return path_value_description(property_name,
                                      self.path_to_check)

    def _main_after_checking_existence_of_dir(self, environment: InstructionEnvironmentForPostSdsStep):
        raise NotImplementedError('abstract method')

    def __main_that_reports_result_via_exceptions(self, environment: InstructionEnvironmentForPostSdsStep):
        self.__assert_path_is_existing_directory(environment)
        self._main_after_checking_existence_of_dir(environment)

    def __assert_path_is_existing_directory(self, environment: InstructionEnvironmentForPostSdsStep):
        expect_existing_dir = file_properties.must_exist_as(file_properties.FileType.DIRECTORY,
                                                            True)

        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        failure_message = file_ref_check.pre_or_post_sds_failure_message_or_none(
            file_ref_check.FileRefCheck(self.path_to_check,
                                        expect_existing_dir),
            path_resolving_env)
        if failure_message is not None:
            raise pfh_ex_method.PfhFailException(failure_message)


class _InstructionForNumFiles(_InstructionBase):
    def __init__(self,
                 settings: _Settings,
                 operator_and_r_operand: IntegerComparisonOperatorAndRightOperand):
        super().__init__(settings.path_to_check)
        self.comparison_handler = comparison_structures.ComparisonHandler(
            self._property_descriptor(_NUM_FILES_PROPERTY_NAME),
            settings.expectation_type,
            NumFilesResolver(settings.path_to_check,
                             settings.file_selector),
            operator_and_r_operand.operator,
            operator_and_r_operand.right_operand)

    def symbol_usages(self) -> list:
        return self.comparison_handler.references

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return return_svh_via_exceptions.translate_svh_exception_to_svh(self.comparison_handler.validate_pre_sds,
                                                                        environment)

    def _main_after_checking_existence_of_dir(self, environment: InstructionEnvironmentForPostSdsStep):
        self.comparison_handler.execute(environment)


class _InstructionForEmptiness(_InstructionBase):
    def __init__(self, settings: _Settings):
        super().__init__(settings.path_to_check)
        self.settings = settings

    def symbol_usages(self) -> list:
        return self.settings.path_to_check.references

    def _main_after_checking_existence_of_dir(self, environment: InstructionEnvironmentForPostSdsStep):
        checker = _EmptinessChecker(self._property_descriptor(_EMPTINESS_PROPERTY_NAME),
                                    environment,
                                    self.settings)
        checker.main()


class _EmptinessChecker:
    def __init__(self,
                 property_descriptor: PropertyDescriptor,
                 environment: InstructionEnvironmentForPostSdsStep,
                 settings: _Settings):
        self.property_descriptor = property_descriptor
        self.environment = environment
        self.path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        self.settings = settings

    def main(self):
        files_in_dir = self._files_in_dir_to_check()

        if self.settings.expectation_type is ExpectationType.POSITIVE:
            self._fail_if_path_dir_is_not_empty(files_in_dir)
        else:
            self._fail_if_path_dir_is_empty(files_in_dir)

    def _files_in_dir_to_check(self) -> list:
        path_to_check = self.settings.path_to_check.resolve_value_of_any_dependency(self.path_resolving_env)
        assert isinstance(path_to_check, pathlib.Path), 'Resolved value should be a path'
        return list(dir_contents_selection.get_selection(path_to_check,
                                                         self.settings.file_selector))

    def _fail_if_path_dir_is_not_empty(self, files_in_dir: list):
        num_files_in_dir = len(files_in_dir)
        if num_files_in_dir != 0:
            self._fail_with_err_msg(str(num_files_in_dir) + ' files',
                                    self._get_description_of_actual(files_in_dir))

    def _fail_if_path_dir_is_empty(self, files_in_dir: list):
        num_files_in_dir = len(files_in_dir)
        if num_files_in_dir == 0:
            self._fail_with_err_msg('empty', [])

    def _fail_with_err_msg(self,
                           actual: str,
                           description_of_actual: list):
        msg = self._failure(actual, description_of_actual).render()
        raise pfh_ex_method.PfhFailException(msg)

    def _failure(self,
                 actual: str,
                 description_of_actual: list,
                 ) -> diff_msg.ExpectedAndActualFailure:
        return diff_msg.ExpectedAndActualFailure(
            self.property_descriptor.description(self.environment),
            self.settings.expectation_type,
            'empty',
            actual,
            description_of_actual)

    def _get_description_of_actual(self, actual_files_in_dir: list) -> list:
        return ['Actual contents:'] + self._dir_contents_err_msg_lines(actual_files_in_dir)

    @staticmethod
    def _dir_contents_err_msg_lines(actual_files_in_dir: list) -> list:
        if len(actual_files_in_dir) < 50:
            actual_files_in_dir.sort()
        num_files_to_display = 5
        ret_val = actual_files_in_dir[:num_files_to_display]
        if len(actual_files_in_dir) > num_files_to_display:
            ret_val.append('...')
        return ret_val


class NumFilesResolver(comparison_structures.OperandResolver):
    def __init__(self,
                 path_to_check: FileRefResolver,
                 file_selector: dir_contents_selection.Selectors):
        super().__init__(_NUM_FILES_PROPERTY_NAME)
        self.path_to_check = path_to_check
        self.file_selector = file_selector

    @property
    def references(self) -> list:
        return self.path_to_check.references

    def resolve(self, environment: InstructionEnvironmentForPostSdsStep) -> int:
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        path_to_check = self.path_to_check.resolve_value_of_any_dependency(path_resolving_env)
        assert isinstance(path_to_check, pathlib.Path), 'Resolved value should be a path'
        selected_files = dir_contents_selection.get_selection(path_to_check, self.file_selector)
        return len(list(selected_files))


_PATH_ARGUMENT = a.Named('PATH')

ACTUAL_RELATIVITY_CONFIGURATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        rel_opts_configuration.PathRelativityVariants({
            RelOptionType.REL_CWD,
            RelOptionType.REL_HOME_ACT,
            RelOptionType.REL_TMP,
            RelOptionType.REL_ACT,
        },
            True),
        RelOptionType.REL_CWD),
    _PATH_ARGUMENT.name,
    True)

_SINGLE_LINE_DESCRIPTION = 'Tests the contents of a directory'

_MAIN_DESCRIPTION_REST = """\
FAIL if {checked_file} is not an existing directory
(even when the assertion is negated).


If {selection} is given, then the test applies to the selected files from the directory.


Symbolic links are followed.
"""

_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY = """\
Tests that {checked_file} is an empty directory, or that the set of selected files is empty.
"""

_CHECKS_THAT_DIRECTORY_CONTAINS_SPECIFIED_NUMBER_OF_FILES = """\
Tests that {checked_file} is a directory that contains the specified number of files.
"""

_PATH_SYNTAX_ELEMENT_DESCRIPTION_TEXT = "The directory who's contents is checked."

_ADDITIONAL_TEXT_OF_NEGATION_SED = ' (Except for the test of the existence of the checked directory.)'
