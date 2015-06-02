"""
Main program for shellcheck
"""
import sys

from shellcheck_lib.cli import parse_command_line_and_execute_test_case

result = parse_command_line_and_execute_test_case.execute(sys.argv[1:])
print(result.full_result.status.name)
sys.exit(result.full_result.status.value)
