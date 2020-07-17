from abc import ABC
from typing import Sequence, List

from exactly_lib.actors.util.executor_made_of_parts import parts
from exactly_lib.actors.util.executor_made_of_parts.sub_process_executor import \
    OsProcessExecutor
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.actor import AtcOsProcessExecutor
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import SymbolUser
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import sh
from exactly_lib.test_case_utils.parse import parse_string


class SourceInfo(SymbolUser):
    def __init__(self, source: StringSdv):
        self.source = source

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self.source.references


class Parser(parts.ExecutableObjectParser[SourceInfo]):
    def apply(self, instructions: Sequence[ActPhaseInstruction]) -> SourceInfo:
        from exactly_lib.util.str_.misc_formatting import lines_content_with_os_linesep
        raw_source = lines_content_with_os_linesep(self._all_source_code_lines(instructions))
        source_sdv = parse_string.string_sdv_from_string(raw_source)
        return SourceInfo(source_sdv)

    @staticmethod
    def _all_source_code_lines(act_phase_instructions) -> List[str]:
        ret_val = []
        for instruction in act_phase_instructions:
            assert isinstance(instruction, ActPhaseInstruction)
            for line in instruction.source_code().lines:
                ret_val.append(line)
        return ret_val


class ActSourceFileNameGenerator:
    """
    Generates the file name for the source of the act phase.

    NOTE: This class was introduced to reduce dependency on SourceInterpreterSetup
    and SourceFileManager, which both feel a bit odd.
    Perhaps these classes (together with this class) can be redesigned to become clearer.
    """

    def base_name(self) -> str:
        raise NotImplementedError()


class ActSourceFileNameGeneratorForConstantFileName(ActSourceFileNameGenerator):
    def __init__(self, base_name: str):
        self._base_name = base_name

    def base_name(self) -> str:
        return self._base_name


class ExecutorBase(OsProcessExecutor, ABC):
    """
    Base class for executors that executes source code by putting it in a file
    and then interpreting this file.
    """

    def __init__(self,
                 os_process_executor: AtcOsProcessExecutor,
                 file_name_generator: ActSourceFileNameGenerator,
                 source_info: SourceInfo,
                 ):
        super().__init__(os_process_executor)
        self.file_name_generator = file_name_generator
        self.source_code_sdv = source_info.source
        self.source_file_path = None

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                ) -> sh.SuccessOrHardError:
        self._set_source_file_path(environment)
        resolving_env = environment.path_resolving_environment_pre_or_post_sds
        source_code = self.source_code_sdv.resolve_value_of_any_dependency(resolving_env)
        try:
            with self.source_file_path.open('w') as f:
                f.write(source_code)
            return sh.new_sh_success()
        except OSError as ex:
            return sh.new_sh_hard_error__str(str(ex))

    def _set_source_file_path(self, environment: InstructionEnvironmentForPostSdsStep):
        root_dir = environment.tmp_dir__path_access.paths_access.new_path_as_existing_dir()
        base_name = self.file_name_generator.base_name()
        self.source_file_path = root_dir / base_name
