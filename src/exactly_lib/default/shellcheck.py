import sys

from exactly_lib.default.default_main_program_setup import default_main_program


def main() -> int:
    return default_main_program().execute(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
