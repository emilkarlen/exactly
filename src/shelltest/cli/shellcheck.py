import sys

from . import parse_command_line_and_execute_test_case


def main(argv: list):
    result = parse_command_line_and_execute_test_case.execute(argv)
    print(result.full_result.status.name)
    sys.exit(result.full_result.status.value)


if __name__ == '__main__':
    main(sys.argv)
