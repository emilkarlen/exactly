from exactly_lib.appl_env.application_environment import ApplicationEnvironment
from exactly_lib.appl_env.os_services import OsServices
from exactly_lib.symbol.logic import resolving_helper
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.logic.resolving_helper import LogicTypeResolvingHelper
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep


def resolving_helper_for_instruction_env(os_services: OsServices,
                                         environment: InstructionEnvironmentForPostSdsStep,
                                         ) -> LogicTypeResolvingHelper:
    return resolving_helper.resolving_helper__of_full_env(
        full_resolving_env_for_instruction_env(os_services,
                                               environment)
    )


def full_resolving_env_for_instruction_env(os_services: OsServices,
                                           environment: InstructionEnvironmentForPostSdsStep,
                                           ) -> FullResolvingEnvironment:
    return FullResolvingEnvironment(
        environment.symbols,
        environment.tcds,
        ApplicationEnvironment(
            os_services,
            environment.proc_exe_settings,
            environment.tmp_dir__path_access.paths_access,
        ),
    )
