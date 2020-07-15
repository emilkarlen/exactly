import pathlib
from typing import Sequence, List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.definitions import instruction_arguments, formatting
from exactly_lib.definitions.argument_rendering.path_syntax import the_path_of
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.entity import concepts
from exactly_lib.instructions.utils.documentation import src_dst
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case import exception_detection
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.test_case.result import sh, svh
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.test_case_file_structure import path_relativity
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import rel_opts_configuration
from exactly_lib.test_case_utils.parse.token_parser_extra import TokenParserExtra
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.textformat.structure.core import ParagraphItem


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


REL_OPTION_ARG_CONF_FOR_SOURCE = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        path_relativity.PathRelativityVariants({RelOptionType.REL_HDS_CASE,
                                                RelOptionType.REL_HDS_ACT},
                                               True),
        RelOptionType.REL_HDS_CASE),
    instruction_arguments.SOURCE_PATH_ARGUMENT.name,
    path_suffix_is_required=True)

REL_OPTION_ARG_CONF_FOR_DESTINATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        path_relativity.PathRelativityVariants({RelOptionType.REL_CWD,
                                                RelOptionType.REL_ACT,
                                                RelOptionType.REL_TMP},
                                               True),
        RelOptionType.REL_CWD),
    instruction_arguments.DESTINATION_PATH_ARGUMENT.name,
    path_suffix_is_required=False)


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase):
    def __init__(self, name: str):
        format_map = {
            'current_dir': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
            'sandbox': formatting.concept_(concepts.SDS_CONCEPT_INFO),
            'SOURCE': instruction_arguments.SOURCE_PATH_ARGUMENT.name,
            'DESTINATION': instruction_arguments.DESTINATION_PATH_ARGUMENT.name,
        }
        super().__init__(name, format_map)
        self._doc_elements = src_dst.DocumentationElements(
            format_map,
            REL_OPTION_ARG_CONF_FOR_SOURCE,
            the_path_of('an existing file or directory.'),
            REL_OPTION_ARG_CONF_FOR_DESTINATION,
            the_path_of('an existing directory, or a non-existing file.')
        )

    def single_line_description(self) -> str:
        return self._tp.format('Copies files and directories into the {sandbox}')

    def main_description_rest(self) -> List[ParagraphItem]:
        return self._tp.fnap(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY,
                         instruction_arguments.SOURCE_PATH_ARGUMENT),
                a.Single(a.Multiplicity.OPTIONAL,
                         instruction_arguments.DESTINATION_PATH_ARGUMENT)]
            ),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return self._doc_elements.syntax_element_descriptions()

    def see_also_targets(self) -> List[CrossReferenceId]:
        return self._doc_elements.see_also_targets()


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> SetupPhaseInstruction:
        parser = TokenParserExtra(TokenStream(rest_of_line))
        src_path = parser.consume_path(REL_OPTION_ARG_CONF_FOR_SOURCE)
        if parser.is_at_eol:
            return _InstallSourceWithoutExplicitDestinationInstruction(src_path)
        dst_path = parser.consume_path(REL_OPTION_ARG_CONF_FOR_DESTINATION)
        parser.report_superfluous_arguments_if_not_at_eol()
        return _InstallSourceWithExplicitDestinationInstruction(src_path,
                                                                dst_path)


class _InstallInstructionBase(SetupPhaseInstruction):
    def __init__(self,
                 source_path: PathSdv):
        self.source_path = source_path

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        path = self._src_path(environment)
        if not path.exists():
            return svh.new_svh_validation_error__str('File does not exist: ' + str(path))
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        raise NotImplementedError()

    def _src_path(self,
                  environment: InstructionEnvironmentForPreSdsStep) -> pathlib.Path:
        return self.source_path.resolve(environment.symbols).value_pre_sds(environment.hds)


class _InstallSourceWithoutExplicitDestinationInstruction(_InstallInstructionBase):
    def __init__(self, source_path: PathSdv):
        super().__init__(source_path)

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self.source_path.references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        src_path = self._src_path(environment)
        destination_container = pathlib.Path.cwd()
        return exception_detection.return_success_or_hard_error(_install_into_directory,
                                                                os_services,
                                                                src_path,
                                                                src_path.name,
                                                                destination_container)


class _InstallSourceWithExplicitDestinationInstruction(_InstallInstructionBase):
    def __init__(self,
                 source_path: PathSdv,
                 destination_path: PathSdv):
        super().__init__(source_path)
        self.destination_path = destination_path

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return tuple(self.source_path.references) + tuple(self.destination_path.references)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        src_path = self._src_path(environment)
        dst_path = self.destination_path.resolve(environment.symbols).value_post_sds(environment.sds)
        main = _MainWithExplicitDestination(os_services, src_path, dst_path)
        return exception_detection.return_success_or_hard_error(main)


class _MainWithExplicitDestination:
    def __init__(self,
                 os_services: OsServices,
                 src_path: pathlib.Path,
                 dst_path: pathlib.Path):
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
                raise exception_detection.DetectedException(
                    FailureDetails.new_constant_message(err_msg))
        else:
            self.os_services.make_dir_if_not_exists__detect_ex(self.dst_path.parent)
            _install_into_directory(self.os_services,
                                    self.src_path,
                                    self.dst_path.name,
                                    self.dst_path.parent)


def _install_into_directory(os_services: OsServices,
                            src_file_path: pathlib.Path,
                            dst_file_name: str,
                            dst_container_path: pathlib.Path):
    target = dst_container_path / dst_file_name
    if target.exists():
        raise exception_detection.DetectedException(
            FailureDetails.new_message(
                text_docs.single_line(
                    str_constructor.FormatMap(
                        '{dst} already exists: {target}',
                        {
                            'dst': instruction_arguments.DESTINATION_PATH_ARGUMENT.name,
                            'target': target,
                        }))
            )
        )
    src = str(src_file_path)
    dst = str(target)
    if src_file_path.is_dir():
        os_services.copy_tree_preserve_as_much_as_possible__detect_ex(src, dst)
    else:
        os_services.copy_file_preserve_as_much_as_possible__detect_ex(src, dst)


_MAIN_DESCRIPTION_REST = """\
  * If {DESTINATION} is not given

    {SOURCE} is installed in the {current_dir},
    as a file/directory with the basename of {SOURCE}.


  * If {DESTINATION} is given, but does not exist
  
    {SOURCE} is copied as a file/directory with the path of {DESTINATION}

    (the basename of {SOURCE} is not preserved).


  * If {DESTINATION} does exist
  
    it must be a directory, and {SOURCE} is copied into that directory,
    as a file/directory with the basename of {SOURCE}.


As many attributes as possible of the copied files are preserved
(this depends on the Python implementation).
"""
