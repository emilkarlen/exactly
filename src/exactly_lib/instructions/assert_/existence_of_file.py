from typing import Sequence, List, Optional

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.argument_rendering import path_syntax
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.path_resolver import PathResolver
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction, WithAssertPhasePurpose
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.result import pfh, svh
from exactly_lib.test_case.validation import pre_or_post_value_validation
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_utils import file_properties, negation_of_predicate, path_check
from exactly_lib.test_case_utils.description_tree import bool_trace_rendering
from exactly_lib.test_case_utils.err_msg2 import env_dep_texts
from exactly_lib.test_case_utils.err_msg2 import path_err_msgs
from exactly_lib.test_case_utils.err_msg2.env_dep_text import TextResolver
from exactly_lib.test_case_utils.err_msg2.header_rendering import SimpleHeaderMinorBlockRenderer
from exactly_lib.test_case_utils.err_msg2.path_rendering import HeaderAndPathMajorBlock, \
    PathRepresentationsRenderersForPrimitive
from exactly_lib.test_case_utils.file_matcher import file_matcher_models
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.file_matcher import resolvers  as fm_resolvers
from exactly_lib.test_case_utils.parse import parse_path
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util import strings
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.structure import MajorBlock
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

        path_to_check = parse_path.parse_path_from_token_parser(_REL_OPTION_CONFIG,
                                                                parser)

        file_matcher = self._parse_optional_file_matcher(parser)

        parser.consume_current_line_as_string_of_remaining_part_of_current_line()

        return _Instruction(expectation_type, path_to_check, file_matcher)

    @staticmethod
    def _parse_optional_file_matcher(parser: token_stream_parser.TokenParser
                                     ) -> Optional[FileMatcherResolver]:
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
                 path_resolver: PathResolver,
                 file_matcher: Optional[FileMatcherResolver]):
        self._expectation_type = expectation_type
        self._path_resolver = path_resolver
        self._file_matcher = file_matcher

        self._symbol_usages = list(path_resolver.references)
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
        try:
            return _Assertion(environment,
                              self._expectation_type,
                              self._path_resolver,
                              self._file_matcher).apply()
        except HardErrorException as ex:
            return pfh.new_pfh_hard_error(ex.error)

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
                 path_resolver: PathResolver,
                 file_matcher: Optional[FileMatcherResolver]
                 ):
        self.environment = environment
        self.expectation_type = expectation_type
        self.path_resolver = path_resolver
        self.file_matcher = file_matcher

        self.described_path = (
            self.path_resolver.resolve(self.environment.symbols)
                .value_of_any_dependency__d(environment.home_and_sds)
        )

    def apply(self) -> pfh.PassOrFailOrHardError:
        if self.file_matcher is None:
            return self._assert_without_file_matcher()
        else:
            return self._assert_with_file_matcher()

    def _path_renderer(self) -> Renderer[MajorBlock]:
        return HeaderAndPathMajorBlock(
            SimpleHeaderMinorBlockRenderer(_ERROR_MESSAGE_HEADER),
            PathRepresentationsRenderersForPrimitive(self.described_path.describer),
        )

    def _assert_without_file_matcher(self) -> Optional[pfh.PassOrFailOrHardError]:
        check = _FILE_EXISTENCE_CHECK
        if self.expectation_type is ExpectationType.NEGATIVE:
            check = file_properties.negation_of(check)

        mb_failure = path_check.failure_message_or_none(check,
                                                        self.described_path)

        return (
            pfh.new_pfh_pass()
            if mb_failure is None
            else pfh.new_pfh_fail(mb_failure)
        )

    def _assert_with_file_matcher(self) -> pfh.PassOrFailOrHardError:
        mb_failure_of_existence = path_check.failure_message_or_none(_FILE_EXISTENCE_CHECK,
                                                                     self.described_path)

        if mb_failure_of_existence is not None:
            return (pfh.new_pfh_fail(mb_failure_of_existence)
                    if self._is_positive_check()
                    else pfh.new_pfh_pass()
                    )

        return self._file_exists_but_must_also_satisfy_file_matcher()

    def _file_exists_but_must_also_satisfy_file_matcher(self) -> pfh.PassOrFailOrHardError:
        matching_result = self._matches_file_matcher_for_expectation_type()
        if matching_result.value:
            return pfh.new_pfh_pass()
        else:
            err_msg = rend_comb.SequenceR([
                path_err_msgs.line_header_block__primitive(
                    strings.FormatMap('Existing {PATH} does not satisfy {FILE_MATCHER}',
                                      _EXISTING_PATH_FAILURE_FORMAT_MAP),
                    self.described_path.describer,
                ),
                bool_trace_rendering.BoolTraceRenderer(matching_result.trace),
            ])

            return pfh.new_pfh_fail(err_msg)

    def _matches_file_matcher_for_expectation_type(self) -> MatchingResult:
        resolver = self._file_matcher_for_expectation_type()

        fm = resolver.resolve(self.environment.symbols).value_of_any_dependency(self.environment.home_and_sds)

        model = file_matcher_models.FileMatcherModelForPrimitivePath(
            self.environment.phase_logging.space_for_instruction(),
            self.described_path)

        return fm.matches_w_trace(model)

    def _file_matcher_for_expectation_type(self) -> FileMatcherResolver:
        return (self.file_matcher
                if self._is_positive_check()
                else fm_resolvers.FileMatcherNotResolver(self.file_matcher)
                )

    def _is_positive_check(self) -> bool:
        return self.expectation_type is ExpectationType.POSITIVE

    def _err_msg_for(self, msg_resolver: ErrorMessageResolver) -> TextRenderer:
        return self._err_msg_for__td(env_dep_texts.of_old(msg_resolver))

    def _err_msg_for__td(self, msg_resolver: TextResolver) -> TextRenderer:
        return msg_resolver.resolve_sequence()


_ERROR_MESSAGE_HEADER = 'Failure for path:'

_FILE_EXISTS_BUT_INVALID_PROPERTIES_ERR_MSG_HEADER = rend_comb.SingletonSequenceR(
    rend_comb.ConstantR(text_struct.LineElement(text_struct.StringLineObject('File exists, but:')))
)

_EXISTING_PATH_FAILURE_FORMAT_MAP = {
    'PATH': syntax_elements.PATH_SYNTAX_ELEMENT.singular_name,
    'FILE_MATCHER': syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
}

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
