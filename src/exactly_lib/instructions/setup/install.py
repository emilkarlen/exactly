import pathlib

from exactly_lib.common.instruction_documentation import InvokationVariant
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.present_working_directory import PRESENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.structures import paras


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        self.dst_arg = a.Named('DESTINATION')
        super().__init__(name, {
            'home_dir': formatting.concept(HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
            'current_dir': formatting.concept(PRESENT_WORKING_DIRECTORY_CONCEPT.name().singular),
            'DESTINATION': self.dst_arg.name,
        })

    def single_line_description(self) -> str:
        return self._format('Install existing files from the {home_dir} into the {current_dir}')

    def main_description_rest(self) -> list:
        text = """\
            As many attributes as possible of the copied files are preserved
            (this depends on Python implementation).


            Mimics the behaviour of Unix cp, when a {DESTINATION} is given.

            If {DESTINATION} does not exist, then the source is installed under the name {DESTINATION}.

            If {DESTINATION} does exist, it must be a directory, and FILE is installed inside that directory.


            NOTE: {DESTINATION}:s with multiple path components are NOT handled intelligently.
            The behaviour is undefined.
            """
        return dt.paths_uses_posix_syntax() + self._paragraphs(text)

    def invokation_variants(self) -> list:
        dst_arg_usage = a.Single(a.Multiplicity.OPTIONAL, self.dst_arg)
        return [
            InvokationVariant(self._cl_syntax_for_args([
                a.Single(a.Multiplicity.MANDATORY, dt.FILE_ARGUMENT),
                dst_arg_usage,
            ]),
                paras('Installs a plain file.')),
            InvokationVariant(self._cl_syntax_for_args([
                a.Single(a.Multiplicity.MANDATORY, dt.DIR_ARGUMENT),
                dst_arg_usage,
            ]),
                paras("Installs the directory and its contents.")),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            dt.a_path_that_is_relative_the(dt.FILE_ARGUMENT,
                                           HOME_DIRECTORY_CONFIGURATION_PARAMETER),
            dt.a_path_that_is_relative_the(dt.DIR_ARGUMENT,
                                           HOME_DIRECTORY_CONFIGURATION_PARAMETER),
            dt.a_path_that_is_relative_the(self.dst_arg,
                                           PRESENT_WORKING_DIRECTORY_CONCEPT),
        ]

    def see_also(self) -> list:
        return [
            HOME_DIRECTORY_CONFIGURATION_PARAMETER.cross_reference_target(),
            PRESENT_WORKING_DIRECTORY_CONCEPT.cross_reference_target(),
        ]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
        num_arguments = len(arguments)
        if num_arguments == 0 or num_arguments > 2:
            msg = 'Invalid number of arguments (one or two expected), found {}'.format(str(num_arguments))
            raise SingleInstructionInvalidArgumentException(msg)
        if num_arguments == 1:
            return _InstallSourceWithoutExplicitDestinationInstruction(arguments[0])
        else:
            return _InstallSourceWithExplicitDestinationInstruction(arguments[0],
                                                                    arguments[1])


class _InstallInstructionBase(SetupPhaseInstruction):
    def __init__(self,
                 source_file_name: str):
        self.source_file_name = source_file_name

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
        return environment.home_directory / self.source_file_name


class _InstallSourceWithoutExplicitDestinationInstruction(_InstallInstructionBase):
    def __init__(self, source_file_name: str):
        super().__init__(source_file_name)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        src_path = self._src_path(environment)
        cwd = pathlib.Path()
        return _install_into_directory(os_services,
                                       src_path,
                                       src_path.name,
                                       cwd)


class _InstallSourceWithExplicitDestinationInstruction(_InstallInstructionBase):
    def __init__(self,
                 source_file_name: str,
                 destination_file_name: str):
        super().__init__(source_file_name)
        self.destination_file_name = destination_file_name

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        src_path = self._src_path(environment)
        basename = src_path.name
        cwd = pathlib.Path()
        direct_target = cwd / self.destination_file_name
        if direct_target.exists():
            if direct_target.is_dir():
                return _install_into_directory(os_services,
                                               src_path,
                                               basename,
                                               direct_target)
            else:
                return sh.new_sh_hard_error('Destination file already exists: {}'.format(direct_target))
        else:
            return _install_into_directory(os_services,
                                           src_path,
                                           self.destination_file_name,
                                           cwd)


def _install_into_directory(os_services: OsServices,
                            src_file_path: pathlib.Path,
                            dst_file_name: str,
                            dst_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
    target = dst_dir_path / dst_file_name
    if target.exists():
        return sh.new_sh_hard_error('Destination already exists: {}'.format(target))
    src = str(src_file_path)
    dst = str(target)
    if src_file_path.is_dir():
        return os_services.copy_tree_preserve_as_much_as_possible(src, dst)
    else:
        return os_services.copy_file_preserve_as_much_as_possible(src, dst)
