from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.instruction.result import sh


class OsServicesThatRaises(OsServices):
    def copy_preserve_as_much_as_possible(self, src: str, dst: str) -> sh.SuccessOrHardError:
        raise NotImplementedError('Should never be used')
