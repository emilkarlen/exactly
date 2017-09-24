import pathlib

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.multi_phase_instructions.utils import file_creation
from exactly_lib.instructions.multi_phase_instructions.utils import instruction_embryo as embryo
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForErrorMessageStringResultAsHardError
from exactly_lib.named_element.resolver_structure import LinesTransformerResolver
from exactly_lib.named_element.symbol.path_resolver import FileRefResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import from_parse_source, \
    TokenParserPrime
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils import file_ref_check
from exactly_lib.test_case_utils.lines_transformer.parse_lines_transformer import \
    parse_lines_transformer_from_token_parser
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerConstant
from exactly_lib.test_case_utils.lines_transformer.transformers import IdentityLinesTransformer
from exactly_lib.test_case_utils.parse.parse_file_ref import parse_file_ref_from_token_parser
from exactly_lib.test_case_utils.parse.rel_opts_configuration import argument_configuration_for_file_creation, \
    RelOptionArgumentConfiguration, RelOptionsConfiguration
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator, SingleStepValidator, \
    ValidationStep
from exactly_lib.util.cli_syntax.elements import argument as a


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        super().__init__(name, {})

    def single_line_description(self) -> str:
        return 'Transforms an existing file into a new file'

    def main_description_rest(self) -> list:
        return []

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                a.Single(a.Multiplicity.MANDATORY,
                         instruction_arguments.SOURCE_PATH_ARGUMENT),
                a.Single(a.Multiplicity.MANDATORY,
                         instruction_arguments.DESTINATION_PATH_ARGUMENT),
                a.Single(a.Multiplicity.OPTIONAL,
                         instruction_arguments.LINES_TRANSFORMER_ARGUMENT),
            ]
            )),
        ]

    def syntax_element_descriptions(self) -> list:
        return []

    def _see_also_cross_refs(self) -> list:
        from exactly_lib.help_texts.entity import types
        return [
            types.LINES_TRANSFORMER_CONCEPT_INFO.cross_reference_target
        ]


class TheInstruction(embryo.InstructionEmbryo):
    def __init__(self,
                 src_path: FileRefResolver,
                 dst_path: FileRefResolver,
                 transformer: LinesTransformerResolver):
        self._src_path = src_path
        self._dst_path = dst_path
        self._transformer = transformer

        self._src_file_validator = file_ref_check.FileRefCheckValidator(
            file_ref_check.FileRefCheck(src_path,
                                        file_properties.must_exist_as(file_properties.FileType.REGULAR,
                                                                      follow_symlinks=True)))

    @property
    def symbol_usages(self) -> list:
        return (self._src_path.references +
                self._dst_path.references +
                self._transformer.references)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return SingleStepValidator(ValidationStep.PRE_SDS,
                                   self._src_file_validator)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices) -> str:
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        src_validation_res = self._src_file_validator.validate_post_sds_if_applicable(path_resolving_env)
        if src_validation_res:
            return src_validation_res
        transformer = self._transformer.resolve(path_resolving_env.symbols)
        src_path = self._src_path.resolve_value_of_any_dependency(path_resolving_env)

        def write_file(output_file):
            with src_path.open() as in_file:
                for line in transformer.transform(path_resolving_env.home_and_sds, in_file):
                    output_file.write(line)

        return file_creation.create_file(self._dst_path,
                                         path_resolving_env,
                                         write_file)

    def _main_with_valid_paths(self,
                               src_path: pathlib.Path,
                               dst_path: pathlib.Path,
                               environment: InstructionEnvironmentForPostSdsStep,
                               logging_paths: PhaseLoggingPaths,
                               os_services: OsServices):
        raise NotImplementedError('abstract method')


class EmbryoParser(embryo.InstructionEmbryoParser):
    def __init__(self, src_rel_opt_arg_conf: RelOptionArgumentConfiguration):
        self._src_rel_opt_arg_conf = src_rel_opt_arg_conf

    def parse(self, source: ParseSource) -> TheInstruction:
        with from_parse_source(source, consume_last_line_if_is_at_eof_after_parse=True) as token_parser:
            assert isinstance(token_parser, TokenParserPrime)  # Type info for IDE
            src_file = parse_file_ref_from_token_parser(self._src_rel_opt_arg_conf, token_parser)
            dst_file = parse_file_ref_from_token_parser(DST_REL_OPT_ARG_CONF, token_parser)
            lines_transformer = self._parse_transformer(token_parser)
            token_parser.report_superfluous_arguments_if_not_at_eol()
            token_parser.consume_current_line_as_plain_string()
            return TheInstruction(src_file, dst_file, lines_transformer)

    @staticmethod
    def _parse_transformer(token_parser: TokenParserPrime) -> LinesTransformerResolver:
        if token_parser.is_at_eol:
            return LinesTransformerConstant(IdentityLinesTransformer())
        else:
            return parse_lines_transformer_from_token_parser(token_parser)


def embryo_parser(phase_is_before_act: bool) -> embryo.InstructionEmbryoParser:
    rel_option_types = _SRC_REL_OPTIONS__BEFORE_ACT if phase_is_before_act else _SRC_REL_OPTIONS__AFTER_ACT
    return EmbryoParser(_src_rel_opt_arg_conf(rel_option_types))


def parts_parser(phase_is_before_act: bool) -> PartsParserFromEmbryoParser:
    return PartsParserFromEmbryoParser(
        embryo_parser(phase_is_before_act),
        MainStepResultTranslatorForErrorMessageStringResultAsHardError())


SRC_PATH_ARGUMENT = instruction_arguments.SOURCE_PATH_ARGUMENT
DST_PATH_ARGUMENT = instruction_arguments.DESTINATION_PATH_ARGUMENT


def _src_rel_opt_arg_conf(rel_option_types: set) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(
        RelOptionsConfiguration(PathRelativityVariants(
            rel_option_types,
            True),
            RelOptionType.REL_CWD),
        SRC_PATH_ARGUMENT.name,
        True)


DST_REL_OPT_ARG_CONF = argument_configuration_for_file_creation(DST_PATH_ARGUMENT.name)

_SRC_REL_OPTIONS__BEFORE_ACT = set(RelOptionType).difference({RelOptionType.REL_RESULT})

_SRC_REL_OPTIONS__AFTER_ACT = set(RelOptionType)
