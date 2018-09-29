from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment


def err_msg_env_from_instr_env(
        instruction_env: InstructionEnvironmentForPostSdsStep) -> ErrorMessageResolvingEnvironment:
    return ErrorMessageResolvingEnvironment(instruction_env.home_and_sds,
                                            instruction_env.symbols)
