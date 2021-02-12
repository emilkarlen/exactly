import pathlib
from typing import Sequence, List, Optional

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args, InvokationVariant, \
    SyntaxElementDescription
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.parts import failure_details
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions import instruction_arguments, formatting
from exactly_lib.definitions.argument_rendering.path_syntax import the_path_of
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.impls import file_properties
from exactly_lib.impls.exception import hard_error_transl
from exactly_lib.impls.instructions import source_file_relativities
from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.impls.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.impls.instructions.multi_phase.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForTextRendererAsHardError
from exactly_lib.impls.instructions.multi_phase.utils.instruction_parts import InstructionPartsParser
from exactly_lib.impls.instructions.utils.documentation import src_dst
from exactly_lib.impls.types.path import path_check, parse_path, rel_opts_configuration
from exactly_lib.impls.types.path.rel_opts_configuration import argument_configuration_for_file_creation, \
    RelOptionArgumentConfiguration
from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, \
    TokenParser
from exactly_lib.section_document.model import SectionContents
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs import path_relativity
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.result import sh
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.sdv import sdv_validation
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.util.textformat.structure.core import ParagraphItem


def parts_parser(phase_is_after_act: bool) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(EmbryoParser(phase_is_after_act),
                                       MainStepResultTranslatorForTextRendererAsHardError())


REL_OPTION_ARG_CONF_FOR_DESTINATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        path_relativity.PathRelativityVariants(
            path_relativity.DEPENDENCY_DICT[path_relativity.DirectoryStructurePartition.NON_HDS]
            - {RelOptionType.REL_RESULT},
            False),
        RelOptionType.REL_CWD),
    instruction_arguments.DESTINATION_PATH_ARGUMENT.name,
    path_suffix_is_required=False)


def src_rel_opt_arg_conf_for_phase(phase_is_after_act: bool) -> RelOptionArgumentConfiguration:
    return source_file_relativities.src_rel_opt_arg_conf_for_phase(
        RelOptionType.REL_HDS_CASE,
        instruction_arguments.SOURCE_PATH_ARGUMENT.name,
        phase_is_after_act
    )


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str,
                 phase_is_after_act: bool):
        super().__init__(name, {})
        self._src_rel_opt_arg_conf = src_rel_opt_arg_conf_for_phase(phase_is_after_act)
        format_map = {
            'current_dir': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
            'sandbox': formatting.concept_(concepts.SDS_CONCEPT_INFO),
            'SOURCE': self._src_rel_opt_arg_conf.argument.name,
            'DESTINATION': REL_OPTION_ARG_CONF_FOR_DESTINATION.argument.name,
        }
        super().__init__(name, format_map)
        self._doc_elements = src_dst.DocumentationElements(
            format_map,
            self._src_rel_opt_arg_conf,
            the_path_of('an existing file or directory.'),
            REL_OPTION_ARG_CONF_FOR_DESTINATION,
            the_path_of('an existing directory, or a non-existing path.')
        )

    def single_line_description(self) -> str:
        return self._tp.format('Copies files and directories into the {sandbox}')

    def main_description_rest(self) -> List[ParagraphItem]:
        return self._tp.fap(_MAIN_DESCRIPTION_REST)

    def notes(self) -> SectionContents:
        return self._tp.section_contents(_NOTES)

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY,
                         self._src_rel_opt_arg_conf.argument),
                a.Single(a.Multiplicity.OPTIONAL,
                         REL_OPTION_ARG_CONF_FOR_DESTINATION.argument)]
            ),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return self._doc_elements.syntax_element_descriptions()

    def see_also_targets(self) -> List[CrossReferenceId]:
        return (
                self._doc_elements.see_also_targets() +
                [concepts.SDS_CONCEPT_INFO.cross_reference_target]
        )


class TheInstructionEmbryoBase(embryo.PhaseAgnosticInstructionEmbryo[Optional[TextRenderer]]):
    def __init__(self, source_path: PathSdv):
        self.source_path = source_path

        def get_ddv_validator(symbols: SymbolTable) -> DdvValidator:
            return path_check.PathCheckDdvValidator(
                path_check.PathCheckDdv(self.source_path.resolve(symbols),
                                        file_properties.must_exist())
            )

        self._validator = sdv_validation.SdvValidatorFromDdvValidator(get_ddv_validator)

    @property
    def validator(self) -> SdvValidator:
        return self._validator

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             ) -> Optional[TextRenderer]:
        sh_result = self._main(environment, os_services)
        return (
            None
            if sh_result.is_success
            else
            sh_result.failure_message
        )

    def _main(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              ) -> sh.SuccessOrHardError:
        pass

    def _src_path(self, environment: InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        return self.source_path.resolve(environment.symbols).value_of_any_dependency(environment.tcds)


class _CopySourceWithoutExplicitDestinationInstruction(TheInstructionEmbryoBase):
    def __init__(self, source_path: PathSdv):
        super().__init__(source_path)

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self.source_path.references

    def _main(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              ) -> sh.SuccessOrHardError:
        src_path = self._src_path(environment)
        destination_container = pathlib.Path.cwd()
        return hard_error_transl.return_success_or_hard_error(_install_into_directory,
                                                              os_services,
                                                              src_path,
                                                              src_path.name,
                                                              destination_container)


class _CopySourceWithExplicitDestinationInstruction(TheInstructionEmbryoBase):
    def __init__(self,
                 source_path: PathSdv,
                 destination_path: PathSdv,
                 ):
        super().__init__(source_path)
        self.destination_path = destination_path

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return tuple(self.source_path.references) + tuple(self.destination_path.references)

    def _main(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              ) -> sh.SuccessOrHardError:
        src_path = self._src_path(environment)
        dst_path = self.destination_path.resolve(environment.symbols).value_post_sds(environment.sds)
        main = _MainWithExplicitDestination(os_services, src_path, dst_path)
        return hard_error_transl.return_success_or_hard_error(main)


class _MainWithExplicitDestination:
    def __init__(self,
                 os_services: OsServices,
                 src_path: pathlib.Path,
                 dst_path: pathlib.Path,
                 ):
        self.os_services = os_services
        self.src_path = src_path
        self.dst_path = dst_path

    def __call__(self, *args, **kwargs):
        src_basename = self.src_path.name
        if self.dst_path.exists():
            if self.dst_path.is_dir():
                _install_into_directory(self.os_services,
                                        self.src_path,
                                        src_basename,
                                        self.dst_path)
            else:
                err_msg = '{} file already exists but is not a directory: {}'.format(
                    instruction_arguments.DESTINATION_PATH_ARGUMENT.name,
                    self.dst_path)
                raise HardErrorException(
                    failure_details.FailureDetailsRenderer(
                        failure_details.FailureDetails.new_constant_message(err_msg))
                )
        else:
            self.os_services.make_dir_if_not_exists(self.dst_path.parent)
            _install_into_directory(self.os_services,
                                    self.src_path,
                                    self.dst_path.name,
                                    self.dst_path.parent)


class EmbryoParser(embryo.InstructionEmbryoParserWoFileSystemLocationInfo[Optional[TextRenderer]]):
    def __init__(self, phase_is_after_act: bool):
        self._src_path_parser = parse_path.PathParser(src_rel_opt_arg_conf_for_phase(phase_is_after_act))
        self._dst_path_parser = parse_path.PathParser(REL_OPTION_ARG_CONF_FOR_DESTINATION)

    def _parse(self, source: ParseSource) -> TheInstructionEmbryoBase:
        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True) as token_parser:
            return self._parse_from_tokens(token_parser)

    def _parse_from_tokens(self, token_parser: TokenParser) -> TheInstructionEmbryoBase:
        src_path = self._src_path_parser.parse_from_token_parser(token_parser)
        if token_parser.is_at_eol:
            return _CopySourceWithoutExplicitDestinationInstruction(src_path)
        dst_path = self._dst_path_parser.parse_from_token_parser(token_parser)
        token_parser.report_superfluous_arguments_if_not_at_eol()
        return _CopySourceWithExplicitDestinationInstruction(src_path, dst_path)


_DST_PATH_ARGUMENT = syntax_elements.PATH_SYNTAX_ELEMENT.argument

REL_OPT_ARG_CONF = argument_configuration_for_file_creation(_DST_PATH_ARGUMENT.name)


def _install_into_directory(os_services: OsServices,
                            src_file_path: pathlib.Path,
                            dst_file_name: str,
                            dst_container_path: pathlib.Path):
    target = dst_container_path / dst_file_name
    if target.exists():
        raise HardErrorException(
            failure_details.FailureDetailsRenderer(
                failure_details.FailureDetails.new_message(
                    text_docs.single_line(
                        str_constructor.FormatMap(
                            '{dst} already exists: {target}',
                            {
                                'dst': instruction_arguments.DESTINATION_PATH_ARGUMENT.name,
                                'target': target,
                            }))
                )
            )
        )
    src = str(src_file_path)
    dst = str(target)
    if src_file_path.is_dir():
        os_services.copy_tree__preserve_as_much_as_possible(src, dst)
    else:
        os_services.copy_file__preserve_as_much_as_possible(src, dst)


_MAIN_DESCRIPTION_REST = """\
  * If {DESTINATION} is not given

    {SOURCE} is installed in the {current_dir},
    as a file/directory with the basename of {SOURCE}.


  * If {DESTINATION} is given, but does not exist
  
    {SOURCE} is copied as a file/directory with the path of {DESTINATION}

    (the basename of {SOURCE} is not preserved).


    Intermediate directories as created, if required.


  * If {DESTINATION} does exist
  
    it must be a directory, and {SOURCE} is copied into that directory,
    as a file/directory with the basename of {SOURCE}.
"""

_NOTES = """\
If given, {DESTINATION} must appear on the same line as {SOURCE}.


As many attributes as possible of the copied files are preserved
(this depends on the Python implementation).
"""
