import os.path
from typing import Sequence, List, Optional

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args, InvokationVariant, \
    SyntaxElementDescription
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.argument_rendering import path_syntax
from exactly_lib.definitions.argument_rendering.path_syntax import the_path_of
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.instructions.multi_phase.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForTextRendererAsHardError
from exactly_lib.instructions.multi_phase.utils.instruction_parts import InstructionPartsParser
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.file_maker import FileMaker
from exactly_lib.instructions.utils.parse.parse_file_maker import CONTENTS_ASSIGNMENT_TOKEN, CONTENTS_ARGUMENT, \
    InstructionConfig, parse_file_contents, \
    FileContentsDocumentation, \
    _src_rel_opt_arg_conf_for_phase
from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, \
    TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreSds
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths, \
    InstructionSourceInfo
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.err_msg2 import path_err_msgs
from exactly_lib.symbol.data.impl.path import described_path_resolvers
from exactly_lib.test_case_utils.parse import parse_file_ref
from exactly_lib.test_case_utils.parse.rel_opts_configuration import argument_configuration_for_file_creation
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


def parts_parser(instruction_name: str,
                 phase_is_after_act: bool) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(EmbryoParser(instruction_name, phase_is_after_act),
                                       MainStepResultTranslatorForTextRendererAsHardError())


RUN_PROGRAM_TOKEN = instruction_names.RUN_INSTRUCTION_NAME


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str,
                 phase_is_after_act: bool):
        super().__init__(name, {})
        self._src_rel_opt_arg_conf = _src_rel_opt_arg_conf_for_phase(phase_is_after_act)
        self._file_contents_doc = FileContentsDocumentation(phase_is_after_act, CONTENTS_ARGUMENT)

        self._tp = TextParser({
            'CONTENTS': CONTENTS_ARGUMENT,
        })

    def single_line_description(self) -> str:
        return 'Creates a file'

    def invokation_variants(self) -> List[InvokationVariant]:
        arguments = path_syntax.mandatory_path_with_optional_relativity(
            _DST_PATH_ARGUMENT,
            REL_OPT_ARG_CONF.path_suffix_is_required)
        contents_arg = a.Single(a.Multiplicity.MANDATORY,
                                a.Named(CONTENTS_ARGUMENT))
        assignment_arg = a.Single(a.Multiplicity.MANDATORY,
                                  a.Constant(CONTENTS_ASSIGNMENT_TOKEN))
        return [
            invokation_variant_from_args(arguments,
                                         docs.paras('Creates an empty file.')),
            invokation_variant_from_args(arguments + [assignment_arg, contents_arg],
                                         self._tp.paras('Creates a file with contents given by {CONTENTS}.')),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        ret_val = [
            rel_path_doc.path_element(_DST_PATH_ARGUMENT.name,
                                      REL_OPT_ARG_CONF.options,
                                      docs.paras(the_path_of('a non-existing file.'))),
        ]
        ret_val += self._file_contents_doc.syntax_element_descriptions()

        return ret_val

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [syntax_elements.PATH_SYNTAX_ELEMENT.cross_reference_target] + self._file_contents_doc.see_also_targets()


class TheInstructionEmbryo(embryo.InstructionEmbryo):
    def __init__(self,
                 path_to_create: FileRefResolver,
                 file_maker: FileMaker):
        self._path_to_create = path_to_create
        self._validator = pre_or_post_validation.all_of([
            _DstFileNameValidator(path_to_create),
            file_maker.validator,
        ])
        self._file_maker = file_maker

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return tuple(self._path_to_create.references) + tuple(self._file_maker.symbol_references)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices) -> Optional[TextRenderer]:
        described_path = described_path_resolvers.of(self._path_to_create) \
            .resolve__with_cwd_as_cd(environment.symbols) \
            .value_of_any_dependency(environment.home_and_sds)
        return self._file_maker.make(environment, os_services, described_path)


class EmbryoParser(embryo.InstructionEmbryoParserWoFileSystemLocationInfo):
    def __init__(self,
                 instruction_name: str,
                 phase_is_after_act: bool):
        self._phase_is_after_act = phase_is_after_act
        self._instruction_name = instruction_name

    def _parse(self, source: ParseSource) -> TheInstructionEmbryo:
        first_line_number = source.current_line_number
        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True) as parser:
            assert isinstance(parser, TokenParser)  # Type info for IDE

            path_to_create = parse_file_ref.parse_file_ref_from_token_parser(REL_OPT_ARG_CONF, parser)
            instruction_config = InstructionConfig(
                InstructionSourceInfo(first_line_number,
                                      self._instruction_name),
                _src_rel_opt_arg_conf_for_phase(self._phase_is_after_act),
                CONTENTS_ARGUMENT
            )

            file_maker = parse_file_contents(instruction_config, parser)

            return TheInstructionEmbryo(path_to_create, file_maker)


class _DstFileNameValidator(PreOrPostSdsValidator):
    def __init__(self, path_to_create: FileRefResolver):
        self._path_to_create = path_to_create

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        path_value__d = described_path_resolvers.of(self._path_to_create).resolve__with_unknown_cd(environment.symbols)
        path_value = path_value__d.value
        suffix = path_value.path_suffix()
        suffix_path = path_value.path_suffix_path()

        suffix_value = suffix.value()
        if suffix_value == '' or suffix_path.name == '':
            return path_err_msgs.line_header__value(
                _PATH_IS_DIR,
                path_value__d.describer
            )

        (head, tail) = os.path.split(suffix_value)
        if tail in _RELATIVE_DIR_NAMES:
            return path_err_msgs.line_header__value(
                _PATH_IS_RELATIVE_DIR,
                path_value__d.describer,
            )

        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        return None


_DST_PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

REL_OPT_ARG_CONF = argument_configuration_for_file_creation(_DST_PATH_ARGUMENT.name)

_PATH_IS_DIR = 'Path to create must not be an existing directory'

_PATH_IS_RELATIVE_DIR = 'Path to create must not be a relative directory'

_RELATIVE_DIR_NAMES = {'.', '..'}
