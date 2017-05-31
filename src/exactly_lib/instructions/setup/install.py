import pathlib

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.current_working_directory import CURRENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help_texts.names import formatting
from exactly_lib.instructions.utils.arg_parse import rel_opts_configuration
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.section_document.parser_implementations.token_stream_parse import TokenParser
from exactly_lib.symbol.concrete_values import FileRefResolver
from exactly_lib.test_case import exception_detection
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.test_case_file_structure import path_relativity
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.failure_details import new_failure_details_from_message


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


OPTION_ARGUMENT_FOR_DESTINATION = a.Named('DESTINATION')

OPTION_ARGUMENT_FOR_SOURCE = a.Named('SOURCE')

REL_OPTION_ARG_CONF_FOR_SOURCE = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        path_relativity.PathRelativityVariants({RelOptionType.REL_HOME},
                                               True),
        True,
        RelOptionType.REL_HOME),
    OPTION_ARGUMENT_FOR_SOURCE.name,
    path_suffix_is_required=True)

REL_OPTION_ARG_CONF_FOR_DESTINATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        path_relativity.PathRelativityVariants({RelOptionType.REL_CWD,
                                                RelOptionType.REL_ACT,
                                                RelOptionType.REL_TMP},
                                               True),
        True,
        RelOptionType.REL_CWD),
    OPTION_ARGUMENT_FOR_DESTINATION.name,
    path_suffix_is_required=False)


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        super().__init__(name, {
            'home_dir': formatting.concept(HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
            'current_dir': formatting.concept(CURRENT_WORKING_DIRECTORY_CONCEPT.name().singular),
            'sandbox': formatting.concept(SANDBOX_CONCEPT.name().singular),
            'SOURCE': OPTION_ARGUMENT_FOR_SOURCE.name,
            'DESTINATION': OPTION_ARGUMENT_FOR_DESTINATION.name,
        })

    def single_line_description(self) -> str:
        return self._format('Install existing files from the {home_dir} into the {sandbox}')

    def main_description_rest(self) -> list:
        return self._paragraphs(_MAIN_DESCRIPTION_REST) + dt.paths_uses_posix_syntax()

    def invokation_variants(self) -> list:
        dst_arg_usage = a.Single(a.Multiplicity.OPTIONAL, OPTION_ARGUMENT_FOR_DESTINATION)
        return [
            InvokationVariant(self._cl_syntax_for_args([
                a.Single(a.Multiplicity.MANDATORY, OPTION_ARGUMENT_FOR_SOURCE),
                dst_arg_usage]
            )),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            dt.a_path_that_is_relative_the(OPTION_ARGUMENT_FOR_SOURCE.name,
                                           HOME_DIRECTORY_CONFIGURATION_PARAMETER),
            dt.a_path_that_is_relative_the(OPTION_ARGUMENT_FOR_DESTINATION.name,
                                           CURRENT_WORKING_DIRECTORY_CONCEPT),
        ]

    def _see_also_cross_refs(self) -> list:
        return [
            HOME_DIRECTORY_CONFIGURATION_PARAMETER.cross_reference_target(),
            CURRENT_WORKING_DIRECTORY_CONCEPT.cross_reference_target(),
        ]


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> SetupPhaseInstruction:
        parser = TokenParser(TokenStream2(rest_of_line))
        src_file_ref = parser.consume_file_ref(REL_OPTION_ARG_CONF_FOR_SOURCE)
        if parser.is_at_eol:
            return _InstallSourceWithoutExplicitDestinationInstruction(src_file_ref)
        dst_file_ref = parser.consume_file_ref(REL_OPTION_ARG_CONF_FOR_DESTINATION)
        parser.report_superfluous_arguments_if_not_at_eol()
        return _InstallSourceWithExplicitDestinationInstruction(src_file_ref,
                                                                dst_file_ref)


class _InstallInstructionBase(SetupPhaseInstruction):
    def __init__(self,
                 source_file_ref: FileRefResolver):
        self.source_file_ref = source_file_ref

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        path = self._src_path(environment)
        if not path.exists():
            return svh.new_svh_validation_error('File does not exist: {}'.format(str(path)))
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        raise NotImplementedError()

    def _src_path(self,
                  environment: InstructionEnvironmentForPreSdsStep) -> pathlib.Path:
        return self.source_file_ref.resolve(environment.symbols).file_path_pre_sds(environment.home_directory)


class _InstallSourceWithoutExplicitDestinationInstruction(_InstallInstructionBase):
    def __init__(self, source_file_ref: FileRefResolver):
        super().__init__(source_file_ref)

    def symbol_usages(self) -> list:
        return self.source_file_ref.references

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
                 source_file_ref: FileRefResolver,
                 destination_file_ref: FileRefResolver):
        super().__init__(source_file_ref)
        self.destination_file_ref = destination_file_ref

    def symbol_usages(self) -> list:
        return self.source_file_ref.references + self.destination_file_ref.references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        src_path = self._src_path(environment)
        dst_path = self.destination_file_ref.resolve(environment.symbols).file_path_post_sds(environment.sds)
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
                err_msg = 'Destination file already exists as a non-directory: {}'.format(self.dst_path)
                raise exception_detection.DetectedException(
                    new_failure_details_from_message(err_msg))
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
            new_failure_details_from_message('Destination already exists: {}'.format(target)))
    src = str(src_file_path)
    dst = str(target)
    if src_file_path.is_dir():
        os_services.copy_tree_preserve_as_much_as_possible__detect_ex(src, dst)
    else:
        os_services.copy_file_preserve_as_much_as_possible__detect_ex(src, dst)


_MAIN_DESCRIPTION_REST = """\
    As many attributes as possible of the copied files are preserved
    (this depends on Python implementation).


    If {DESTINATION} is not given, then {SOURCE} is installed in the {current_dir},
    as a file/directory with the name basename({SOURCE}).
    

    If {DESTINATION} is given, but does not exist, then the {SOURCE} is installed as
    a file/directory with the name {DESTINATION}
    
    (the basename of {SOURCE} is not preserved).


    If {DESTINATION} does exist, it must be a directory, and {SOURCE} is installed inside that directory
    as a file/directory with the same base name as {SOURCE}.
    """
