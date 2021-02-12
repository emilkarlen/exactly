import os.path
from typing import Sequence, List, Optional

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args, InvokationVariant, \
    SyntaxElementDescription
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions import file_types
from exactly_lib.definitions.argument_rendering import path_syntax
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.impls.instructions.multi_phase.new_file import defs
from exactly_lib.impls.instructions.multi_phase.new_file import file_maker
from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.impls.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.impls.instructions.multi_phase.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForTextRendererAsHardError
from exactly_lib.impls.instructions.multi_phase.utils.instruction_parts import InstructionPartsParser
from exactly_lib.impls.types.path import path_err_msgs, parse_path, relative_path_options_documentation as rel_path_doc
from exactly_lib.impls.types.path.rel_opts_configuration import argument_configuration_for_file_creation
from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, \
    TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreSds
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.type_val_deps.dep_variants.sdv import sdv_validation
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


def parts_parser(phase_is_after_act: bool) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(EmbryoParser(phase_is_after_act),
                                       MainStepResultTranslatorForTextRendererAsHardError())


RUN_PROGRAM_TOKEN = instruction_names.RUN_INSTRUCTION_NAME


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str,
                 phase_is_after_act: bool):
        super().__init__(name, {})
        self._src_rel_opt_arg_conf = defs.src_rel_opt_arg_conf_for_phase(phase_is_after_act)

        self._tp = TextParser({
            'CONTENTS': syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT.singular_name,
        })

    def single_line_description(self) -> str:
        return 'Creates ' + file_types.REGULAR.singular_determined

    def invokation_variants(self) -> List[InvokationVariant]:
        arguments = path_syntax.mandatory_path_with_optional_relativity(
            _DST_PATH_ARGUMENT,
            REL_OPT_ARG_CONF.path_suffix_is_required)
        contents_arg = syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT.single_mandatory
        assignment_arg = a.Single(a.Multiplicity.MANDATORY,
                                  a.Constant(defs.CONTENTS_ASSIGNMENT_TOKEN))
        return [
            invokation_variant_from_args(arguments,
                                         docs.paras('Creates an empty file.')),
            invokation_variant_from_args(arguments + [assignment_arg, contents_arg],
                                         self._tp.paras('Creates a file with contents given by {CONTENTS}.')),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return [
            rel_path_doc.path_element(_DST_PATH_ARGUMENT.name,
                                      REL_OPT_ARG_CONF.options),
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            syntax_elements.PATH_SYNTAX_ELEMENT.cross_reference_target,
            syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT.cross_reference_target
        ]


class _TheInstructionEmbryo(embryo.PhaseAgnosticInstructionEmbryo[Optional[TextRenderer]]):
    def __init__(self,
                 path_to_create: PathSdv,
                 file_maker_: file_maker.FileMaker,
                 ):
        self._path_to_create = path_to_create
        self._validator = sdv_validation.all_of([
            _DstFileNameSdvValidator(path_to_create),
            file_maker_.validator,
        ])
        self._file_maker = file_maker_

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return tuple(self._path_to_create.references) + tuple(self._file_maker.symbol_references)

    @property
    def validator(self) -> SdvValidator:
        return self._validator

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             ) -> Optional[TextRenderer]:
        described_path = (
            self._path_to_create.resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds)
        )
        return self._file_maker.make(environment, os_services, described_path)


class EmbryoParser(embryo.InstructionEmbryoParserWoFileSystemLocationInfo[Optional[TextRenderer]]):
    def __init__(self, phase_is_after_act: bool):
        self._path_parser = parse_path.PathParser(REL_OPT_ARG_CONF)

        self._file_maker_parser = file_maker.FileMakerParser(
            defs.src_rel_opt_arg_conf_for_phase(phase_is_after_act))

    def _parse(self, source: ParseSource) -> _TheInstructionEmbryo:
        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True) as tokens:
            return self._parse_from_tokens(tokens)

    def _parse_from_tokens(self, tokens: TokenParser) -> _TheInstructionEmbryo:
        path_to_create = self._path_parser.parse_from_token_parser(tokens)
        file_maker_ = self._file_maker_parser.parse(tokens)

        tokens.report_superfluous_arguments_if_not_at_eol()

        return _TheInstructionEmbryo(path_to_create, file_maker_)


class _DstFileNameSdvValidator(SdvValidator):
    def __init__(self, path_to_create: PathSdv):
        self._path_to_create = path_to_create

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        path_ddv = self._path_to_create.resolve(environment.symbols)
        suffix = path_ddv.path_suffix()
        suffix_path = path_ddv.path_suffix_path()

        suffix_value = suffix.value()
        if suffix_value == '' or suffix_path.name == '':
            return path_err_msgs.line_header__ddv(
                _PATH_IS_DIR,
                path_ddv.describer()
            )

        (head, tail) = os.path.split(suffix_value)
        if tail in _RELATIVE_DIR_NAMES:
            return path_err_msgs.line_header__ddv(
                _PATH_IS_RELATIVE_DIR,
                path_ddv.describer(),
            )

        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        return None


_DST_PATH_ARGUMENT = syntax_elements.PATH_SYNTAX_ELEMENT.argument

REL_OPT_ARG_CONF = argument_configuration_for_file_creation(_DST_PATH_ARGUMENT.name)

_PATH_IS_DIR = 'Path to create must not be an existing directory'

_PATH_IS_RELATIVE_DIR = 'Path to create must not be a relative directory'

_RELATIVE_DIR_NAMES = {'.', '..'}
