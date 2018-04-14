from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.process_execution.command import Command
from exactly_lib.util.process_execution.execution_elements import Executable


class OsServicesThatRaises(OsServices):
    def copy_file_preserve_as_much_as_possible(self, src: str, dst: str) -> sh.SuccessOrHardError:
        raise NotImplementedError('Should never be used')

    def copy_tree_preserve_as_much_as_possible(self, src: str, dst: str) -> sh.SuccessOrHardError:
        raise NotImplementedError('Should never be used')

    def make_executable__detect_ex(self, command: Command) -> Executable:
        raise NotImplementedError('Should never be used')
