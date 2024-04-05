import argparse
from pathlib import Path
import sys
import subprocess
from typing import List

EXACTLY_NAME = 'exactly'

DIST_SUB_DIR = Path('dist')

DESCRIPTION = 'Installs Exactly from a distribution wheel file, or uninstalls it'

EPILOG = ('Installs only from a wheel file found in PRJ-ROOT/{}/.'
          .format(DIST_SUB_DIR))

PGM_NAME = Path(sys.argv[0]).name

PIP_ARGS = [sys.executable, '-m', 'pip']
PIP_ARGS__INSTALL = ['install', '--upgrade']
PIP_ARGS__UNINSTALL = ['uninstall', '--yes']

PIP_ARGS__VENV = ['--require-virtualenv']

CMD_INSTALL = 'install'
CMD_UNINSTALL = 'uninstall'
CMDS = [CMD_INSTALL, CMD_UNINSTALL]


def exit_error(msg: str):
    print('{}: {}'.format(PGM_NAME, msg))
    sys.exit(1)


def get_dist_dir() -> Path:
    prj_root_dir = Path(sys.path[0]).parent
    ret_val = prj_root_dir / DIST_SUB_DIR
    if not ret_val.is_dir():
        exit_error('Distribution dir does not exist: ' + str(ret_val))
    return ret_val


def get_wheel_file(dist_dir: Path) -> Path:
    whl_files = list(dist_dir.glob('*.whl'))
    num_whl_files = len(whl_files)

    if num_whl_files == 0:
        exit_error('No wheel file to install in dist dir: ' + str(dist_dir))
    if num_whl_files > 1:
        exit_error('More than one wheel files in dist dir: ' + str(dist_dir))

    return whl_files[0]


def args_for_install(venv: bool, whl_file: str) -> List[str]:
    ret_val = list(PIP_ARGS)
    if venv:
        ret_val += PIP_ARGS__VENV
    ret_val += PIP_ARGS__INSTALL
    ret_val += [whl_file]

    return ret_val


def args_for_uninstall(in_venv: bool) -> List[str]:
    ret_val = list(PIP_ARGS)
    if in_venv:
        ret_val += PIP_ARGS__VENV
    ret_val += PIP_ARGS__UNINSTALL
    ret_val += [EXACTLY_NAME]

    return ret_val


def install(in_venv: bool) -> int:
    dist_dir = get_dist_dir()
    whl_file = get_wheel_file(dist_dir)
    args = args_for_install(in_venv, str(whl_file))
    return subprocess.run(args).returncode


def uninstall(in_venv: bool) -> int:
    args = args_for_uninstall(in_venv)
    return subprocess.run(args).returncode


def args_parser() -> argparse.ArgumentParser:
    ret_val = argparse.ArgumentParser(
        prog=PGM_NAME,
        description=DESCRIPTION,
        epilog=EPILOG)
    ret_val.add_argument('command', choices=CMDS,
                         help='What to do')
    ret_val.add_argument('--venv', action='store_true',
                         help='Only work in virtual environments')

    return ret_val


def main():
    args = args_parser().parse_args()
    in_venv = args.venv
    st = 1
    if args.command == CMD_INSTALL:
        st = install(in_venv)
    elif args.command == CMD_UNINSTALL:
        st = uninstall(in_venv)
    else:
        exit_error('Unknown COMMAND: ' + args.command)

    sys.exit(st)


if __name__ == '__main__':
    main()
