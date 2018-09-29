from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment


def path_resolving_env_from_err_msg_env(
        environment: ErrorMessageResolvingEnvironment) -> PathResolvingEnvironmentPreOrPostSds:
    return PathResolvingEnvironmentPreOrPostSds(environment.tcds,
                                                environment.symbols)
