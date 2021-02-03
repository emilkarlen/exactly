from typing import Sequence

from exactly_lib.common.report_rendering.description_tree import rendering__node_wo_data
from exactly_lib.impls.instructions.assert_.utils.instruction_of_matcher import ModelGetterSdv, ModelGetterDdv, \
    ModelGetterAdv, ModelGetter
from exactly_lib.impls.program_execution.processors.store_result_in_files import ExitCodeAndStderrFile, \
    ProcessorThatStoresStderrInFiles
from exactly_lib.impls.types.string_source import as_stdin as str_src_as_stdin
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.program.ddv.program import ProgramDdv, ProgramAdv
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.util.process_execution import file_ctx_managers, process_output_files
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MinorBlock
from exactly_lib.util.symbol_table import SymbolTable


def model_getter(program: ProgramSdv) -> ModelGetterSdv[ExitCodeAndStderrFile]:
    return _ExitCodeAndStderrFileGetterSdv(program)


class _ExitCodeAndStderrFileGetterSdv(ModelGetterSdv[ExitCodeAndStderrFile]):
    def __init__(self, program: ProgramSdv):
        self._program = program

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._program.references

    def resolve(self, symbols: SymbolTable) -> ModelGetterDdv[ExitCodeAndStderrFile]:
        return _ExitCodeAndStderrFileGetterDdv(self._program.resolve(symbols))


class _ExitCodeAndStderrFileGetterDdv(ModelGetterDdv[ExitCodeAndStderrFile]):
    def __init__(self, program: ProgramDdv):
        self._program = program

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ModelGetterAdv[ExitCodeAndStderrFile]:
        return _ExitCodeAndStderrFileGetterAdv(self._program.value_of_any_dependency(tcds))

    @property
    def validator(self) -> DdvValidator:
        return self._program.validator


class _ExitCodeAndStderrFileGetterAdv(ModelGetterAdv[ExitCodeAndStderrFile]):
    def __init__(self, program: ProgramAdv):
        self._program = program

    def primitive(self, environment: ApplicationEnvironment) -> ModelGetter[ExitCodeAndStderrFile]:
        return _ExitCodeAndStderrFileGetter(self._program.primitive(environment), environment)


class _ExitCodeAndStderrFileGetter(ModelGetter[ExitCodeAndStderrFile]):
    def __init__(self,
                 program: Program,
                 app_env: ApplicationEnvironment,
                 ):
        self._program = program
        self._app_env = app_env

    def get(self) -> ExitCodeAndStderrFile:
        processor = ProcessorThatStoresStderrInFiles(
            self._app_env.os_services.command_executor,
            str_src_as_stdin.of_sequence(self._program.stdin, self._app_env.mem_buff_size),
            file_ctx_managers.dev_null(),
            self._app_env.tmp_files_space.new_path(process_output_files.STDERR_FILE_NAME),
        )
        return processor.process(self._app_env.process_execution_settings, self._program.command)

    def description(self) -> SequenceRenderer[MinorBlock]:
        return rendering__node_wo_data.NodeAsMinorBlocksRenderer(self._program.structure())
