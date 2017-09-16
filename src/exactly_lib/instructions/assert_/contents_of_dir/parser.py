import pathlib

from exactly_lib.instructions.assert_.contents_of_dir.config import PATH_ARGUMENT, ACTUAL_RELATIVITY_CONFIGURATION
from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions as pfh_ex_method
from exactly_lib.instructions.assert_.utils.expression import comparison_structures
from exactly_lib.instructions.assert_.utils.expression import parse as expression_parse
from exactly_lib.instructions.assert_.utils.expression import parse as parse_expr
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_EXPECTED_VALUE
from exactly_lib.instructions.utils import return_svh_via_exceptions
from exactly_lib.instructions.utils.parse.token_stream_parse import new_token_parser
from exactly_lib.named_element.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.named_element.resolver_structure import FileMatcherResolver
from exactly_lib.named_element.symbol.path_resolver import FileRefResolver
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import pfh, svh
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils import file_ref_check
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.err_msg.path_description import PathValuePartConstructor
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.type_system.logic import file_matcher as file_matcher_type
from exactly_lib.util.logic_types import ExpectationType
from . import config

_CHECKERS = [
    config.NUM_FILES_CHECK_ARGUMENT,
    config.EMPTINESS_CHECK_ARGUMENT,
]


class Parser(InstructionParserThatConsumesCurrentLine):
    def __init__(self):
        self.format_map = {
            'PATH': PATH_ARGUMENT.name,
        }

    def _parse(self, rest_of_line: str) -> AssertPhaseInstruction:
        tokens = new_token_parser(rest_of_line,
                                  self.format_map)
        path_to_check = tokens.consume_file_ref(ACTUAL_RELATIVITY_CONFIGURATION)
        file_selection = parse_file_matcher.parse_optional_selection_resolver(tokens)
        expectation_type = tokens.consume_optional_negation_operator()
        instructions_parser = _CheckInstructionParser(_Settings(expectation_type,
                                                                path_to_check,
                                                                file_selection))

        instruction = instructions_parser.parse(tokens)
        tokens.report_superfluous_arguments_if_not_at_eol()
        return instruction


class _Settings:
    def __init__(self,
                 expectation_type: ExpectationType,
                 path_to_check: FileRefResolver,
                 file_matcher: FileMatcherResolver):
        self.expectation_type = expectation_type
        self.path_to_check = path_to_check
        self.file_matcher = file_matcher


class _CheckInstructionParser:
    missing_check_description = 'Missing arguments for check (one of {})'.format(
        ', '.join(map(lambda x: '"' + x + '"', _CHECKERS))
    )

    def __init__(self, settings: _Settings):
        self.settings = settings
        self.command_parsers = {
            config.NUM_FILES_CHECK_ARGUMENT: self.parse_num_files_check,
            config.EMPTINESS_CHECK_ARGUMENT: self.parse_empty_check,
        }

    def parse(self, parser: TokenParserPrime) -> AssertPhaseInstruction:
        return parser.parse_mandatory_command(self.command_parsers,
                                              self.missing_check_description)

    def parse_empty_check(self, parser: TokenParserPrime) -> AssertPhaseInstruction:
        return _InstructionForEmptiness(self.settings)

    def parse_num_files_check(self, parser: TokenParserPrime) -> AssertPhaseInstruction:
        cmp_op_and_rhs = expression_parse.parse_integer_comparison_operator_and_rhs(
            parser,
            expression_parse.validator_for_non_negative)

        return _InstructionForNumFiles(self.settings, cmp_op_and_rhs)


class _InstructionBase(AssertPhaseInstruction):
    def __init__(self, settings: _Settings):
        self.settings = settings

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return pfh_ex_method.translate_pfh_exception_to_pfh(self.__main_that_reports_result_via_exceptions,
                                                            environment)

    def _property_descriptor(self, property_name: str) -> property_description.PropertyDescriptor:
        return property_description.PropertyDescriptorWithConstantPropertyName(
            property_name,
            property_description.multiple_object_descriptors([
                PathValuePartConstructor(self.settings.path_to_check),
                parse_file_matcher.SelectorsDescriptor(self.settings.file_matcher),
            ])
        )

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
            file_ref_check.FileRefCheck(self.settings.path_to_check,
                                        expect_existing_dir),
            path_resolving_env)
        if failure_message is not None:
            raise pfh_ex_method.PfhFailException(failure_message)


class _InstructionForNumFiles(_InstructionBase):
    def __init__(self,
                 settings: _Settings,
                 operator_and_r_operand: parse_expr.IntegerComparisonOperatorAndRightOperand):
        super().__init__(settings)
        self.comparison_handler = comparison_structures.ComparisonHandler(
            self._property_descriptor(config.NUM_FILES_PROPERTY_NAME),
            settings.expectation_type,
            NumFilesResolver(settings.path_to_check,
                             settings.file_matcher),
            operator_and_r_operand.operator,
            operator_and_r_operand.right_operand)

    def symbol_usages(self) -> list:
        return self.comparison_handler.references + self.settings.file_matcher.references

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return return_svh_via_exceptions.translate_svh_exception_to_svh(self.comparison_handler.validate_pre_sds,
                                                                        environment)

    def _main_after_checking_existence_of_dir(self, environment: InstructionEnvironmentForPostSdsStep):
        self.comparison_handler.execute(environment)


class _InstructionForEmptiness(_InstructionBase):
    def symbol_usages(self) -> list:
        return self.settings.path_to_check.references + self.settings.file_matcher.references

    def _main_after_checking_existence_of_dir(self, environment: InstructionEnvironmentForPostSdsStep):
        checker = _EmptinessChecker(self._property_descriptor(config.EMPTINESS_PROPERTY_NAME),
                                    environment,
                                    self.settings)
        checker.main()


class _EmptinessChecker:
    def __init__(self,
                 property_descriptor: property_description.PropertyDescriptor,
                 environment: InstructionEnvironmentForPostSdsStep,
                 settings: _Settings):
        self.property_descriptor = property_descriptor
        self.environment = environment
        self.path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        self.settings = settings
        self.error_message_resolver = _ErrorMessageResolver(settings.path_to_check,
                                                            property_descriptor,
                                                            settings.expectation_type,
                                                            EMPTINESS_CHECK_EXPECTED_VALUE)

    def main(self):
        files_in_dir = self._files_in_dir_to_check()

        if self.settings.expectation_type is ExpectationType.POSITIVE:
            self._fail_if_path_dir_is_not_empty(files_in_dir)
        else:
            self._fail_if_path_dir_is_empty(files_in_dir)

    def _files_in_dir_to_check(self) -> list:
        dir_path_to_check = self.settings.path_to_check.resolve_value_of_any_dependency(self.path_resolving_env)
        assert isinstance(dir_path_to_check, pathlib.Path), 'Resolved value should be a path'
        file_matcher = self.settings.file_matcher.resolve(self.path_resolving_env.symbols)
        selected_files = file_matcher_type.matching_files_in_dir(file_matcher, dir_path_to_check)
        return list(selected_files)

    def _fail_if_path_dir_is_not_empty(self, files_in_dir: list):
        num_files_in_dir = len(files_in_dir)
        if num_files_in_dir != 0:
            self._fail_with_err_msg(files_in_dir)

    def _fail_if_path_dir_is_empty(self, files_in_dir: list):
        num_files_in_dir = len(files_in_dir)
        if num_files_in_dir == 0:
            self._fail_with_err_msg(files_in_dir)

    def _fail_with_err_msg(self,
                           files_in_dir: list):
        diff_failure_info = self.error_message_resolver.resolve(files_in_dir, self.environment)
        msg = diff_failure_info.render()
        raise pfh_ex_method.PfhFailException(msg)


class _ErrorMessageResolver:
    def __init__(self,
                 root_dir_path_resolver: FileRefResolver,
                 property_descriptor: property_description.PropertyDescriptor,
                 expectation_type: ExpectationType,
                 expected_description_str: str,
                 ):
        self.expectation_type = expectation_type
        self.property_descriptor = property_descriptor
        self.root_dir_path_resolver = root_dir_path_resolver
        self.expected_description_str = expected_description_str

    def resolve(self,
                actual_files: list,
                environment: InstructionEnvironmentForPostSdsStep) -> diff_msg.DiffFailureInfo:
        return diff_msg.DiffFailureInfo(
            self.property_descriptor.description(environment),
            self.expectation_type,
            self.expected_description_str,
            self.resolve_actual_info(actual_files, environment.path_resolving_environment_pre_or_post_sds))

    def resolve_actual_info(self, actual_files: list,
                            environment: PathResolvingEnvironmentPreOrPostSds) -> diff_msg.ActualInfo:
        num_files_in_dir = len(actual_files)
        single_line_value = str(num_files_in_dir) + ' files'
        return diff_msg.ActualInfo(single_line_value,
                                   self._resolve_description_lines(actual_files, environment))

    def _resolve_description_lines(self,
                                   actual_files: list,
                                   environment: PathResolvingEnvironmentPreOrPostSds) -> list:
        return ['Actual contents:'] + self._dir_contents_err_msg_lines(actual_files, environment)

    def _dir_contents_err_msg_lines(self,
                                    actual_files_in_dir: list,
                                    environment: PathResolvingEnvironmentPreOrPostSds) -> list:
        root_dir_path = self.root_dir_path_resolver.resolve_value_of_any_dependency(environment)
        if len(actual_files_in_dir) < 50:
            actual_files_in_dir.sort()
        num_files_to_display = 5
        ret_val = [
            str(p.relative_to(root_dir_path))
            for p in actual_files_in_dir[:num_files_to_display]
        ]
        if len(actual_files_in_dir) > num_files_to_display:
            ret_val.append('...')
        return ret_val


class NumFilesResolver(comparison_structures.OperandResolver):
    def __init__(self,
                 path_to_check: FileRefResolver,
                 file_matcher: FileMatcherResolver):
        super().__init__(config.NUM_FILES_PROPERTY_NAME)
        self.path_to_check = path_to_check
        self.file_matcher = file_matcher

    @property
    def references(self) -> list:
        return self.path_to_check.references

    def resolve(self, environment: InstructionEnvironmentForPostSdsStep) -> int:
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        path_to_check = self.path_to_check.resolve_value_of_any_dependency(path_resolving_env)
        assert isinstance(path_to_check, pathlib.Path), 'Resolved value should be a path'
        file_matcher = self.file_matcher.resolve(environment.symbols)
        selected_files = file_matcher_type.matching_files_in_dir(file_matcher, path_to_check)
        return len(list(selected_files))
