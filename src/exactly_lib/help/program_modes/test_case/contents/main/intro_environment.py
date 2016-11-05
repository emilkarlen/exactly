from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import \
    OPTION_FOR_KEEPING_SANDBOX_DIRECTORY
from exactly_lib.default.program_modes.test_case.default_instruction_names import CHANGE_DIR_INSTRUCTION_NAME
from exactly_lib.execution.environment_variables import ENV_VAR_ACT
from exactly_lib.help.concepts.plain_concepts.present_working_directory import PRESENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.formatting import emphasis
from exactly_lib.test_case.sandbox_directory_structure import SUB_DIRECTORY__ACT
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import document as doc


def execution_documentation(setup: Setup) -> doc.SectionContents:
    description_text = DESCRIPTION.format(phase=setup.phase_names,
                                          pwd=emphasis(CHANGE_DIR_INSTRUCTION_NAME),
                                          PWD=formatting.concept(PRESENT_WORKING_DIRECTORY_CONCEPT.name().singular),
                                          SANDBOX_ACT_DIR=ENV_VAR_ACT,
                                          act_subdir=SUB_DIRECTORY__ACT,
                                          cli_option_for_keeping_sandbox=OPTION_FOR_KEEPING_SANDBOX_DIRECTORY)
    paragraphs = normalize_and_parse(description_text)
    return doc.SectionContents(paragraphs, [])


DESCRIPTION = """\
Each test case is executed in it's own temporary sandbox directory.
This sandbox is automatically removed after the execution
(unless {cli_option_for_keeping_sandbox} is used).


The sandbox directory contains a sub directory {act_subdir}/, which
is the {PWD} at the start of the test case.


This is the {PWD} for all phases, unless it is changed by the {pwd} instruction.

A change of {PWD} will stay in effect for all following instructions and phases.
"""
