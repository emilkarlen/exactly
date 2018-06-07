from exactly_lib import program_info
from exactly_lib.execution import tmp_dir_resolving
from exactly_lib.execution.tmp_dir_resolving import SandboxRootDirNameResolver


def for_test() -> SandboxRootDirNameResolver:
    return tmp_dir_resolving.mk_tmp_dir_with_prefix(program_info.PROGRAM_NAME + '-test-')


def prefix_for_suite() -> str:
    return program_info.PROGRAM_NAME + 'test-suite-'
