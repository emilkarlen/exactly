import shutil

from shellcheck_lib.test_case.instruction.result import sh


class OsServices:
    """
    Interface to some Operation System Services.

    These are services that should not be implemented as part of instructions, and
    that may vary depending on operating system.
    """

    def copy_file_preserve_as_much_as_possible(self,
                                               src: str,
                                               dst: str) -> sh.SuccessOrHardError:
        raise NotImplementedError()

    def copy_tree_preserve_as_much_as_possible(self,
                                               src: str,
                                               dst: str) -> sh.SuccessOrHardError:
        raise NotImplementedError()


def new_default() -> OsServices:
    return _Default()


class _Default(OsServices):
    def copy_file_preserve_as_much_as_possible(self, src: str, dst: str) -> sh.SuccessOrHardError:
        try:
            shutil.copy2(src, dst)
            return sh.new_sh_success()
        except OSError as ex:
            return sh.new_sh_hard_error('Failed to copy {} -> {}: {}'.format(src, dst, str(ex)))

    def copy_tree_preserve_as_much_as_possible(self, src: str, dst: str) -> sh.SuccessOrHardError:
        try:
            shutil.copytree(src, dst)
            return sh.new_sh_success()
        except OSError as ex:
            return sh.new_sh_hard_error('Failed to copy {} -> {}: {}'.format(src, dst, str(ex)))
