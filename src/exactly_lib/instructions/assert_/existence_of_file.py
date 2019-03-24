from typing import Sequence, List, Optional

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.argument_rendering import path_syntax
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case import pre_or_post_value_validation
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction, WithAssertPhasePurpose
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.result import pfh, svh
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_utils import file_properties, negation_of_predicate
from exactly_lib.test_case_utils.err_msg.path_description import PathValuePartConstructor
from exactly_lib.test_case_utils.file_matcher import file_matcher_models
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.file_matcher import resolvers  as fm_resolvers
from exactly_lib.test_case_utils.file_ref_check import pre_or_post_sds_failure_message_or_none, FileRefCheck
from exactly_lib.test_case_utils.parse import parse_file_ref
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.type_system import error_message
from exactly_lib.type_system.error_message import ErrorMessageResolver, ErrorMessageResolvingEnvironment
from exactly_lib.type_system.logic import hard_error
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.textformat.structure.core import ParagraphItem


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


NEGATION_OPERATOR = instruction_arguments.NEGATION_ARGUMENT_STR

PROPERTIES_SEPARATOR = instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT

_PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

_FILE_EXISTENCE_CHECK = file_properties.must_exist(follow_symlinks=False)

_REL_OPTION_CONFIG = RelOptionArgumentConfiguration(
    RelOptionsConfiguration(
        PathRelativityVariants(
            {RelOptionType.REL_CWD,
             RelOptionType.REL_HOME_ACT,
             RelOptionType.REL_ACT,
             RelOptionType.REL_TMP,
             },
            True),
        RelOptionType.REL_CWD),
    _PATH_ARGUMENT.name,
    True)


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase,
                                  WithAssertPhasePurpose):
    PROPERTIES = a.Named('PROPERTIES')

    def __init__(self, name: str):
        self.negation_argument = a.Constant(NEGATION_OPERATOR)
        super().__init__(name, {
            'PATH': _PATH_ARGUMENT.name,
            'FILE_MATCHER': syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
            'NEGATION_OPERATOR': NEGATION_OPERATOR,
        })

    def single_line_description(self) -> str:
        return 'Tests the existence, and optionally properties, of a file'

    def main_description_rest(self) -> List[ParagraphItem]:
        return self._tp.fnap(_PART_OF_MAIN_DESCRIPTION_REST_THAT_IS_SPECIFIC_FOR_THIS_INSTRUCTION)

    def invokation_variants(self) -> List[InvokationVariant]:
        negation_arguments = [negation_of_predicate.optional_negation_argument_usage()]
        path_arguments = path_syntax.mandatory_path_with_optional_relativity(
            _PATH_ARGUMENT,
            _REL_OPTION_CONFIG.path_suffix_is_required)
        file_matcher_arguments = [a.Single(a.Multiplicity.OPTIONAL, self.PROPERTIES)]

        return [
            invokation_variant_from_args(negation_arguments +
                                         path_arguments +
                                         file_matcher_arguments,
                                         []),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        negation_elements = [
            negation_of_predicate.assertion_syntax_element_description()
        ]
        path_element = rel_path_doc.path_element_2(_REL_OPTION_CONFIG)
        properties_elements = [
            SyntaxElementDescription(self.PROPERTIES.name,
                                     self._tp.fnap(_PROPERTIES_DESCRIPTION),
                                     [self._properties_invokation_variant()]),
        ]

        return negation_elements + [path_element] + properties_elements

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            syntax_elements.PATH_SYNTAX_ELEMENT.cross_reference_target,
            syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.cross_reference_target,
        ]

    @staticmethod
    def _properties_invokation_variant() -> InvokationVariant:
        return invokation_variant_from_args([
            a.Single(a.Multiplicity.MANDATORY, a.Constant(PROPERTIES_SEPARATOR)),
            syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.single_mandatory,
        ])


class Parser(InstructionParserWithoutSourceFileLocationInfo):
    def __init__(self):
        self.format_map = {
            'PATH': _PATH_ARGUMENT.name,
        }

    def parse_from_source(self, source: ParseSource) -> AssertPhaseInstruction:
        with token_stream_parser.from_parse_source(
                source,
                consume_last_line_if_is_at_eof_after_parse=True) as token_parser:
            assert isinstance(token_parser,
                              token_stream_parser.TokenParser), 'Must have a TokenParser'  # Type info for IDE
            return self._parse(token_parser)

    def _parse(self, parser: token_stream_parser.TokenParser) -> AssertPhaseInstruction:
        expectation_type = parser.consume_optional_negation_operator()

        path_to_check = parse_file_ref.parse_file_ref_from_token_parser(_REL_OPTION_CONFIG,
                                                                        parser)

        file_matcher = self._parse_optional_file_matcher(parser)

        parser.consume_current_line_as_string_of_remaining_part_of_current_line()

        return _Instruction(expectation_type, path_to_check, file_matcher)

    @staticmethod
    def _parse_optional_file_matcher(parser: token_stream_parser.TokenParser
                                     ) -> Optional[parse_file_matcher.FileMatcherResolver]:
        file_matcher = None

        if not parser.is_at_eol:
            parser.consume_mandatory_constant_unquoted_string(
                PROPERTIES_SEPARATOR,
                must_be_on_current_line=True)
            file_matcher = parse_file_matcher.parse_resolver(parser, must_be_on_current_line=False)
            parser.report_superfluous_arguments_if_not_at_eol()

        return file_matcher


class _Instruction(AssertPhaseInstruction):
    def __init__(self,
                 expectation_type: ExpectationType,
                 file_ref_resolver: FileRefResolver,
                 file_matcher: Optional[parse_file_matcher.FileMatcherResolver]):
        self._expectation_type = expectation_type
        self._file_ref_resolver = file_ref_resolver
        self._file_matcher = file_matcher

        self._symbol_usages = list(file_ref_resolver.references)
        if file_matcher is not None:
            self._symbol_usages += file_matcher.references

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._symbol_usages

    def validate_pre_sds(self, environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        validator = self._validator(environment)
        maybe_err_msg = validator.validate_pre_sds_if_applicable(environment.hds)
        return svh.new_maybe_svh_validation_error(maybe_err_msg)

    def validate_post_setup(self, environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        validator = self._validator(environment)
        maybe_err_msg = validator.validate_post_sds_if_applicable(environment.home_and_sds)
        return svh.new_maybe_svh_validation_error(maybe_err_msg)

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return _Assertion(environment,
                          self._expectation_type,
                          self._file_ref_resolver,
                          self._file_matcher).apply()

    def _validator(self, environment: InstructionEnvironmentForPreSdsStep
                   ) -> pre_or_post_value_validation.PreOrPostSdsValueValidator:
        if self._file_matcher is None:
            return pre_or_post_value_validation.constant_success_validator()
        else:
            return self._file_matcher.resolve(environment.symbols).validator()


class _Assertion:
    def __init__(self,
                 environment: i.InstructionEnvironmentForPostSdsStep,
                 expectation_type: ExpectationType,
                 file_ref_resolver: FileRefResolver,
                 file_matcher: Optional[parse_file_matcher.FileMatcherResolver]
                 ):
        self.environment = environment
        self.expectation_type = expectation_type
        self.file_ref_resolver = file_ref_resolver
        self.file_matcher = file_matcher

    def apply(self) -> pfh.PassOrFailOrHardError:
        result = self._apply()
        if result.is_error:
            return pfh.PassOrFailOrHardError(
                result.status,
                self._prepend_path_description(result.failure_message))
        else:
            return result

    def _apply(self) -> pfh.PassOrFailOrHardError:
        if self.file_matcher is None:
            return self._assert_without_file_matcher()
        else:
            return self._assert_with_file_matcher()

    def _prepend_path_description(self, msg: str) -> str:
        err_msg_env = ErrorMessageResolvingEnvironment(
            self.environment.home_and_sds,
            self.environment.symbols
        )
        path_lines = PathValuePartConstructor(self.file_ref_resolver).lines(err_msg_env)

        return _ERROR_MESSAGE_HEADER + '\n'.join(path_lines) + '\n\n' + msg

    def _assert_without_file_matcher(self) -> pfh.PassOrFailOrHardError:
        check = _FILE_EXISTENCE_CHECK
        if self.expectation_type is ExpectationType.NEGATIVE:
            check = file_properties.negation_of(check)

        failure_message = pre_or_post_sds_failure_message_or_none(
            FileRefCheck(self.file_ref_resolver,
                         check),
            self.environment.path_resolving_environment_pre_or_post_sds)

        return pfh.new_pfh_fail_if_has_failure_message(failure_message)

    def _assert_with_file_matcher(self) -> pfh.PassOrFailOrHardError:
        failure_message_of_existence = pre_or_post_sds_failure_message_or_none(
            FileRefCheck(self.file_ref_resolver,
                         _FILE_EXISTENCE_CHECK),
            self.environment.path_resolving_environment_pre_or_post_sds)

        if failure_message_of_existence:
            return (pfh.new_pfh_fail(failure_message_of_existence)
                    if self._is_positive_check()
                    else pfh.new_pfh_pass()
                    )

        return self._file_exists_but_must_also_satisfy_file_matcher()

    def _file_exists_but_must_also_satisfy_file_matcher(self) -> pfh.PassOrFailOrHardError:
        try:
            failure_message_resolver = self._matches_file_matcher_for_expectation_type()
            if failure_message_resolver is None:
                return pfh.new_pfh_pass()
            else:
                err_msg = (_FILE_EXISTS_BUT_INVALID_PROPERTIES_ERR_MSG_HEADER +
                           self._err_msg_for(failure_message_resolver))
                return pfh.new_pfh_fail(err_msg)
        except hard_error.HardErrorException as ex:
            return pfh.new_pfh_hard_error(self._err_msg_for(ex.error))

    def _matches_file_matcher_for_expectation_type(self) -> Optional[ErrorMessageResolver]:
        resolver = self._file_matcher_for_expectation_type()

        fm = resolver.resolve(self.environment.symbols).value_of_any_dependency(self.environment.home_and_sds)
        existing_file_path = self.file_ref_resolver \
            .resolve(self.environment.symbols) \
            .value_of_any_dependency(self.environment.home_and_sds)

        model = file_matcher_models.FileMatcherModelForPrimitivePath(
            self.environment.phase_logging.space_for_instruction(),
            existing_file_path)

        return fm.matches2(model)

    def _file_matcher_for_expectation_type(self) -> parse_file_matcher.FileMatcherResolver:
        return (self.file_matcher
                if self._is_positive_check()
                else fm_resolvers.FileMatcherNotResolver(self.file_matcher)
                )

    def _is_positive_check(self) -> bool:
        return self.expectation_type is ExpectationType.POSITIVE

    def _err_msg_for(self, msg_resolver: ErrorMessageResolver) -> str:
        env = error_message.ErrorMessageResolvingEnvironment(self.environment.home_and_sds,
                                                             self.environment.symbols)
        return msg_resolver.resolve(env)


_ERROR_MESSAGE_HEADER = """\
Failure for path:
"""

_FILE_EXISTS_BUT_INVALID_PROPERTIES_ERR_MSG_HEADER = """\
File exists, but:
"""

_PROPERTIES_DESCRIPTION = """\
Applies a {FILE_MATCHER} on {PATH}, if it exists.
"""

_PART_OF_MAIN_DESCRIPTION_REST_THAT_IS_SPECIFIC_FOR_THIS_INSTRUCTION = """\
Symbolic links are not followed in the test of existence
(so a broken symbolic link is considered to exist).


When not negated, the assertion will
PASS if, and only if:

{PATH} exists, and has the specified properties.


When negated, the assertion will
FAIL if, and only if:

{PATH} does not exist, or {PATH} does not have the specified properties.
"""
