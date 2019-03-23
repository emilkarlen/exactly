from typing import Sequence, List, Optional

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.argument_rendering import path_syntax
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.doc_format import syntax_text
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction, WithAssertPhasePurpose
from exactly_lib.test_case.result import pfh
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_utils import file_properties, negation_of_predicate
from exactly_lib.test_case_utils.file_matcher import file_matcher_models
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.file_matcher import resolvers  as fm_resolvers
from exactly_lib.test_case_utils.file_ref_check import pre_or_post_sds_failure_message_or_none, FileRefCheck
from exactly_lib.test_case_utils.parse import parse_file_ref
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.type_system import error_message
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.type_system.logic import hard_error
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render.cli_program_syntax import render_argument
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.textformat.structure import lists, structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.utils import transform_list_to_table


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


NEGATION_OPERATOR = instruction_arguments.NEGATION_ARGUMENT_STR

FILE_TYPE_OPTIONS = [
    (file_type, a.OptionName(long_name=file_info.type_argument))
    for file_type, file_info in file_properties.TYPE_INFO.items()
]

_TYPE_ARGUMENT_STR = 'TYPE'

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
    def __init__(self, name: str):
        self.type_argument = a.Named(_TYPE_ARGUMENT_STR)
        self.negation_argument = a.Constant(NEGATION_OPERATOR)
        super().__init__(name, {
            'PATH': _PATH_ARGUMENT.name,
            'TYPE': _TYPE_ARGUMENT_STR,
            'SYM_LNK': file_properties.TYPE_INFO[file_properties.FileType.SYMLINK].description,
            'NEGATION_OPERATOR': NEGATION_OPERATOR,
        })

    def single_line_description(self) -> str:
        return 'Tests the existence, and optionally type, of a file'

    def main_description_rest(self) -> List[ParagraphItem]:
        return self._tp.fnap(_PART_OF_MAIN_DESCRIPTION_REST_THAT_IS_SPECIFIC_FOR_THIS_INSTRUCTION)

    def invokation_variants(self) -> List[InvokationVariant]:
        type_arguments = [a.Single(a.Multiplicity.OPTIONAL, self.type_argument)]
        negation_arguments = [negation_of_predicate.optional_negation_argument_usage()]
        path_arguments = path_syntax.mandatory_path_with_optional_relativity(
            _PATH_ARGUMENT,
            _REL_OPTION_CONFIG.path_suffix_is_required)
        arguments = negation_arguments + type_arguments + path_arguments

        return [
            invokation_variant_from_args(arguments,
                                         []),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        negation_elements = [
            negation_of_predicate.assertion_syntax_element_description()
        ]
        type_elements = [
            SyntaxElementDescription(self.type_argument.name,
                                     self._type_element_description(), []),
        ]
        path_element = rel_path_doc.path_element_2(_REL_OPTION_CONFIG)
        all_elements = negation_elements + type_elements + [path_element]

        return all_elements

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            syntax_elements.PATH_SYNTAX_ELEMENT.cross_reference_target,
        ]

    def _type_element_description(self) -> List[ParagraphItem]:
        return (self._tp.fnap(_TYPE_ELEMENT_DESCRIPTION_INTRO)
                +
                [transform_list_to_table(self._file_type_list())])

    def _file_type_list(self) -> lists.HeaderContentList:
        def type_description(file_type: file_properties.FileType) -> List[ParagraphItem]:
            text = 'Tests if {PATH} is a {file_type}, or a {SYM_LNK} to a {file_type}.'
            if file_type is file_properties.FileType.SYMLINK:
                text = 'Tests if {PATH} is a {SYM_LNK} (link target may or may not exist).'
            extra = {
                'file_type': file_properties.TYPE_INFO[file_type].description,
            }
            return self._tp.fnap(text, extra)

        sort_value__list_items = [
            (file_properties.TYPE_INFO[file_type],
             docs.list_item(syntax_text(render_argument(a.Option(option_name))),
                            type_description(file_type)))
            for file_type, option_name in FILE_TYPE_OPTIONS]
        sort_value__list_items.sort(key=lambda type_name__list_item: type_name__list_item[0].type_argument)
        list_items = [type_name__list_item[1]
                      for type_name__list_item in sort_value__list_items]
        return lists.HeaderContentList(list_items,
                                       lists.Format(lists.ListType.VARIABLE_LIST))


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

    def _parse_optional_file_matcher(self, parser: token_stream_parser.TokenParser
                                     ) -> Optional[parse_file_matcher.FileMatcherResolver]:
        file_matcher = None

        if not parser.is_at_eol:
            parser.consume_mandatory_constant_unquoted_string(
                instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT,
                must_be_on_current_line=True)
            file_matcher = parse_file_matcher.parse_resolver(parser)
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

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        failure_message_of_existence = pre_or_post_sds_failure_message_or_none(
            FileRefCheck(self._file_ref_resolver,
                         _FILE_EXISTENCE_CHECK),
            environment.path_resolving_environment_pre_or_post_sds)

        if failure_message_of_existence:
            return (pfh.new_pfh_fail(failure_message_of_existence)
                    if self._is_positive_check()
                    else pfh.new_pfh_pass()
                    )

        return (self._file_exists_and_no_file_matcher()
                if self._file_matcher is None
                else self._file_exists_but_must_also_satisfy_file_matcher(environment)
                )

    def _file_exists_and_no_file_matcher(self) -> pfh.PassOrFailOrHardError:
        return (pfh.new_pfh_pass()
                if self._is_positive_check()
                else pfh.new_pfh_fail('File exists TODO improve err msg')
                )

    def _file_exists_but_must_also_satisfy_file_matcher(self, environment: i.InstructionEnvironmentForPostSdsStep
                                                        ) -> pfh.PassOrFailOrHardError:
        try:
            failure_message_resolver = self._matches_file_matcher_for_expectation_type(environment)
            if failure_message_resolver is None:
                return pfh.new_pfh_pass()
            else:
                return pfh.new_pfh_fail(self._err_msg_for(environment, failure_message_resolver))
        except hard_error.HardErrorException as ex:
            return pfh.new_pfh_hard_error(self._err_msg_for(environment, ex.error))

    def _matches_file_matcher_for_expectation_type(self, environment: i.InstructionEnvironmentForPostSdsStep
                                                   ) -> Optional[ErrorMessageResolver]:
        resolver = self._file_matcher_for_expectation_type()

        fm = resolver.resolve(environment.symbols).value_of_any_dependency(environment.home_and_sds)
        existing_file_path = self._file_ref_resolver \
            .resolve(environment.symbols) \
            .value_of_any_dependency(environment.home_and_sds)

        model = file_matcher_models.FileMatcherModelForPrimitivePath(
            environment.phase_logging.space_for_instruction(),
            existing_file_path)

        return fm.matches2(model)

    def _file_matcher_for_expectation_type(self) -> parse_file_matcher.FileMatcherResolver:
        return (self._file_matcher
                if self._is_positive_check()
                else fm_resolvers.FileMatcherNotResolver(self._file_matcher)
                )

    def _is_positive_check(self) -> bool:
        return self._expectation_type is ExpectationType.POSITIVE

    def _err_msg_for(self,
                     environment: i.InstructionEnvironmentForPostSdsStep,
                     msg_resolver: ErrorMessageResolver) -> str:
        env = error_message.ErrorMessageResolvingEnvironment(environment.home_and_sds,
                                                             environment.symbols)
        return msg_resolver.resolve(env)


_TYPE_ELEMENT_DESCRIPTION_INTRO = """\
Includes the file type in the assertion.
"""

_PART_OF_MAIN_DESCRIPTION_REST_THAT_IS_SPECIFIC_FOR_THIS_INSTRUCTION = """\
If {TYPE} is not given, the type of the file is ignored.


When not negated, the assertion will
PASS if, and only if:

{PATH} exists, and is a file of the asserted type.


When negated, the assertion will
FAIL if, and only if:

{PATH} exists, and is a file of the asserted type.
"""
