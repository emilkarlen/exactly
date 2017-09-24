import pathlib

from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.act_phase_setups.util.executor_made_of_parts.sub_process_executor import CommandExecutor
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, SymbolUser
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case_utils.parse import parse_string


class SourceInfo(SymbolUser):
    def __init__(self, source: StringResolver):
        self.source = source

    def symbol_usages(self) -> list:
        return self.source.references


class Parser(parts.Parser):
    def apply(self, act_phase_instructions: list) -> SourceInfo:
        from exactly_lib.util.string import lines_content_with_os_linesep
        raw_source = lines_content_with_os_linesep(self._all_source_code_lines(act_phase_instructions))
        source_resolver = parse_string.string_resolver_from_string(raw_source)
        return SourceInfo(source_resolver)

    @staticmethod
    def _all_source_code_lines(act_phase_instructions) -> list:
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


class ExecutorBase(CommandExecutor):
    """
    Base class for executors that executes source code by putting it in a file
    and then interpreting this file.
    """

    def __init__(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 file_name_generator: ActSourceFileNameGenerator,
                 source_info: SourceInfo):
        super().__init__(os_process_executor)
        self.file_name_generator = file_name_generator
        self.source_code_resolver = source_info.source

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        script_file_path = self._source_file_path(script_output_dir_path)
        resolving_env = environment.path_resolving_environment_pre_or_post_sds
        source_code = self.source_code_resolver.resolve_value_of_any_dependency(resolving_env)
        try:
            with open(str(script_file_path), 'w') as f:
                f.write(source_code)
            return sh.new_sh_success()
        except OSError as ex:
            return sh.new_sh_hard_error(str(ex))

    def _source_file_path(self,
                          script_output_dir_path: pathlib.Path) -> pathlib.Path:
        base_name = self.file_name_generator.base_name()
        return script_output_dir_path / base_name
