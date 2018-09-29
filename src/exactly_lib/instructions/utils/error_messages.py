from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg.error_info import ErrorMessageResolvingEnvironment


def err_msg_env_from_instr_env(
        instruction_env: InstructionEnvironmentForPostSdsStep) -> ErrorMessageResolvingEnvironment:
    return ErrorMessageResolvingEnvironment(instruction_env.home_and_sds,
                                            instruction_env.phase_logging,
                                            instruction_env.symbols)
