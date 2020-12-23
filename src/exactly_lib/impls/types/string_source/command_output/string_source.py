from exactly_lib.common.err_msg import std_err_contents
from exactly_lib.definitions.primitives import program
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.string_source.cached_frozen import StringSourceWithCachedFrozen
from exactly_lib.impls.types.string_source.contents_handler import handler_via_write_to
from exactly_lib.impls.types.string_source.contents_handler.handler import ContentsHandler
from exactly_lib.impls.types.string_source.contents_handler.handler_via_file import ContentsHandlerViaFile
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile


def string_source(structure_header: str,
                  ignore_exit_code: bool,
                  output_channel_to_capture: ProcOutputFile,
                  command: Command,
                  proc_exe_settings: ProcessExecutionSettings,
                  command_executor: CommandExecutor,
                  mem_buff_size: int,
                  tmp_file_space: DirFileSpace,
                  ) -> StringSource:
    constructor_of_structure_builder = ConstructorOfStructureBuilder(
        structure_header,
        ignore_exit_code,
        command.structure_renderer(),
    )
    contents_handler = _contents_handler(
        ignore_exit_code,
        output_channel_to_capture,
        command,
        proc_exe_settings,
        command_executor,
        tmp_file_space,
    )
    return StringSourceWithCachedFrozen(
        constructor_of_structure_builder.new_structure_builder,
        contents_handler,
        mem_buff_size,
        process_output_files.PROC_OUTPUT_FILE_NAMES[output_channel_to_capture],
    )


class ConstructorOfStructureBuilder:
    def __init__(self,
                 structure_header: str,
                 ignore_exit_code: bool,
                 command: StructureRenderer,
                 ):
        self._structure_header = structure_header
        self._ignore_exit_code = ignore_exit_code
        self._command = command

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return StringSourceStructureBuilder(
            self._structure_header,
            (custom_details.optional_option(program.WITH_IGNORED_EXIT_CODE_OPTION_NAME,
                                            self._ignore_exit_code),),
            (self._command,),
        )


def _contents_handler(
        ignore_exit_code: bool,
        output_channel_to_capture: ProcOutputFile,
        command: Command,
        proc_exe_settings: ProcessExecutionSettings,
        command_executor: CommandExecutor,
        tmp_file_space: DirFileSpace,
) -> ContentsHandler:
    if output_channel_to_capture is ProcOutputFile.STDERR and not ignore_exit_code:
        from . import exit_relevant
        return ContentsHandlerViaFile(
            tmp_file_space,
            exit_relevant.StderrFileCreator(
                command,
                proc_exe_settings,
                command_executor,
                std_err_contents.STD_ERR_TEXT_READER,
            ),
        )
    else:
        return handler_via_write_to.ContentsHandlerViaWriteTo(
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
            command: Command,
            proc_exe_settings: ProcessExecutionSettings,
            command_executor: CommandExecutor,
            ) -> handler_via_write_to.Writer:
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
