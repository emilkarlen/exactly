from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.resolving_helper import DataTypeResolvingHelper


def resolving_helper_for_instruction_env(environment: InstructionEnvironmentForPostSdsStep) -> DataTypeResolvingHelper:
    return DataTypeResolvingHelper(
        environment.symbols,
        environment.tcds,
    )
