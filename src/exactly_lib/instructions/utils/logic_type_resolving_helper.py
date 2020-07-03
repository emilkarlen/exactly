from exactly_lib.symbol.logic.resolving_helper import LogicTypeResolvingHelper
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment


def resolving_helper_for_instruction_env(environment: InstructionEnvironmentForPostSdsStep) -> LogicTypeResolvingHelper:
    return LogicTypeResolvingHelper(
        environment.symbols,
        environment.tcds,
        ApplicationEnvironment(environment.application_environment.tmp_files_space),
    )
