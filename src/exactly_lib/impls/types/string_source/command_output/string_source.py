from exactly_lib.common.err_msg import std_err_contents
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import program as program_primitives
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.string_source.cached_frozen import StringSourceWithCachedFrozen
from exactly_lib.impls.types.string_source.contents import contents_via_write_to
from exactly_lib.impls.types.string_source.contents.contents_via_file import ContentsViaFile
from exactly_lib.impls.types.utils.command_w_stdin import CommandWStdin
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile


def string_source(structure_option: str,
                  ignore_exit_code: bool,
                  output_channel_to_capture: ProcOutputFile,
                  command: CommandWStdin,
                  proc_exe_settings: ProcessExecutionSettings,
                  command_executor: CommandExecutor,
                  mem_buff_size: int,
                  tmp_file_space: DirFileSpace,
                  ) -> StringSource:
    constructor_of_structure_builder = ConstructorOfStructureBuilder(
        structure_option,
        ignore_exit_code,
        command.structure(),
    )
    contents = _contents(
        ignore_exit_code,
        output_channel_to_capture,
        command,
        proc_exe_settings,
        command_executor,
        tmp_file_space,
    )
    return StringSourceWithCachedFrozen(
        constructor_of_structure_builder.new_structure_builder,
        contents,
        mem_buff_size,
        process_output_files.PROC_OUTPUT_FILE_NAMES[output_channel_to_capture],
    )


class ConstructorOfStructureBuilder:
    def __init__(self,
                 structure_option: str,
                 ignore_exit_code: bool,
                 command: StructureRenderer,
                 ):
        self._structure_header = ' '.join((structure_option, syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name))
        self._ignore_exit_code = ignore_exit_code
        self._command = command

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return StringSourceStructureBuilder(
            self._structure_header,
            (
                custom_details.optional_option(program_primitives.WITH_IGNORED_EXIT_CODE_OPTION_NAME,
                                               self._ignore_exit_code),
                custom_details.TreeStructure(self._command),
            ),
        )


def _contents(
        ignore_exit_code: bool,
        output_channel_to_capture: ProcOutputFile,
        command: CommandWStdin,
        proc_exe_settings: ProcessExecutionSettings,
        command_executor: CommandExecutor,
        tmp_file_space: DirFileSpace,
) -> StringSourceContents:
    if output_channel_to_capture is ProcOutputFile.STDERR and not ignore_exit_code:
        from . import exit_relevant
        return ContentsViaFile(
            tmp_file_space,
            exit_relevant.StderrFileCreator(
                command,
                proc_exe_settings,
                command_executor,
                std_err_contents.STD_ERR_TEXT_READER,
            ),
        )
    else:
        return contents_via_write_to.ContentsViaWriteTo(
            tmp_file_space,
            _writer(
                ignore_exit_code,
                output_channel_to_capture,
                command,
                proc_exe_settings,
                command_executor,
            ),
            process_output_files.PROC_OUTPUT_FILE_NAMES[output_channel_to_capture],
        )


def _writer(ignore_exit_code: bool,
            output_channel_to_capture: ProcOutputFile,
            command: CommandWStdin,
            proc_exe_settings: ProcessExecutionSettings,
            command_executor: CommandExecutor,
            ) -> contents_via_write_to.Writer:
    if ignore_exit_code:
        from . import exit_ignored
        if output_channel_to_capture is ProcOutputFile.STDOUT:
            return exit_ignored.StdoutWriter(command, proc_exe_settings, command_executor)
        else:
            return exit_ignored.StderrWriter(command, proc_exe_settings, command_executor)
    else:
        from . import exit_relevant
        return exit_relevant.StdoutWriter(command, proc_exe_settings, command_executor,
                                          std_err_contents.STD_ERR_TEXT_READER)
