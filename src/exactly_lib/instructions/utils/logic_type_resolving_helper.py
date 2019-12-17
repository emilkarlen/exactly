from exactly_lib.symbol.logic.resolving_helper import LogicTypeResolvingHelper
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep


def resolving_helper_for_instruction_env(environment: InstructionEnvironmentForPostSdsStep) -> LogicTypeResolvingHelper:
    return LogicTypeResolvingHelper(
        environment.symbols,
        environment.tcds,
        environment.application_environment.tmp_files_space,
    )
