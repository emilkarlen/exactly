import pathlib
import stat


def make_executable_by_os(path: pathlib.Path):
    initial_mode = path.stat().st_mode
    path.chmod(initial_mode | stat.S_IXUSR)
