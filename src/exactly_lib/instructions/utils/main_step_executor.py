from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh


class MainStepExecutor:
    """
    Executes the main step of an instruction in an arbitrary phase.
    """

    def apply_sh(self,
                 environment: GlobalEnvironmentForPostEdsPhase,
                 os_services: OsServices) -> sh.SuccessOrHardError:
        raise NotImplementedError()

    def apply_pfh(self,
                  environment: GlobalEnvironmentForPostEdsPhase,
                  os_services: OsServices) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()
