from shellcheck_lib.cli.cli_environment.command_line_options import OPTION_FOR_KEEPING_SANDBOX_DIRECTORY
from shellcheck_lib.default.program_modes.test_case.default_instruction_names import CHANGE_DIR_INSTRUCTION_NAME
from shellcheck_lib.execution.environment_variables import ENV_VAR_ACT
from shellcheck_lib.execution.execution_directory_structure import SUB_DIRECTORY__ACT
from shellcheck_lib.help.program_modes.test_case.contents.main.utils import Setup
from shellcheck_lib.help.utils.formatting import emphasis
from shellcheck_lib.util.textformat.parse import normalize_and_parse
from shellcheck_lib.util.textformat.structure import document as doc


def execution_documentation(setup: Setup) -> doc.SectionContents:
    description_text = DESCRIPTION.format(phase=setup.phase_names,
                                          pwd=emphasis(CHANGE_DIR_INSTRUCTION_NAME),
                                          SANDBOX_ACT_DIR=ENV_VAR_ACT,
                                          act_subdir=SUB_DIRECTORY__ACT,
                                          cli_option_for_keeping_sandbox=OPTION_FOR_KEEPING_SANDBOX_DIRECTORY)
    paragraphs = normalize_and_parse(description_text)
    return doc.SectionContents(paragraphs, [])


DESCRIPTION = """\
Each test case is executed in it’s own temporary sandbox directory.
This sandbox is automatically removed after the execution
(unless {cli_option_for_keeping_sandbox} is used).


The environment variable {SANDBOX_ACT_DIR} points to a directory inside the sandbox.
The Present Working Directory is set to this directory.

This will be the PWD for all phases, unless it is changed by the {pwd} instruction.

A change of PWD will stay in effect for all following instructions and phases.
"""
