from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.result import sh


class OsServicesThatRaises(OsServices):
    def copy_file_preserve_as_much_as_possible(self, src: str, dst: str) -> sh.SuccessOrHardError:
        raise NotImplementedError('Should never be used')

    def copy_tree_preserve_as_much_as_possible(self, src: str, dst: str) -> sh.SuccessOrHardError:
        raise NotImplementedError('Should never be used')
