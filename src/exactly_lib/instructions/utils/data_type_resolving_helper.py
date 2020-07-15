from exactly_lib.symbol.data.resolving_helper import DataTypeResolvingHelper
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep


def resolving_helper_for_instruction_env(environment: InstructionEnvironmentForPostSdsStep) -> DataTypeResolvingHelper:
    return DataTypeResolvingHelper(
        environment.symbols,
        environment.tcds,
    )
