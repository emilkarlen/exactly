from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCaseHelp


class IntroductionDocumentation:
    def __init__(self, test_case_help: TestCaseHelp):
        self.test_case_help = test_case_help

    def test_cases(self) -> list:
        """
        :return: [ParagraphItem]
        """
        pass


a_test_case_is_a_plain_text_file = """A test case is written as plain text file."""

initial_example = """\
[act]
helloworld
[assert]
exitcode 0
stdout <<EOF
Hello, World!
EOF\
"""

description = """\
A test case file contains a sequence of “phases”.


The “act” phase contains the program/action to test.


By default, the “act” phase must contain a single command line.

(This can be changed. See documentation of [act] (<command for displaying help for the phase “act”).)


All other phases contain “instructions”.
E.g., “exitcode” and “stdout” are instructions of the “assert” phase.


The “act” phase is mandatory. All other phases are optional.


Executing a test case means “executing” all of it’s phases.


The phases are always executed in the same order,
regardless of the order they appear in the test case file.


The phases are, in order of execution:
"""
