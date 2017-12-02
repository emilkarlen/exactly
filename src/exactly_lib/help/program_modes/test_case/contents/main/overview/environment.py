from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import \
    OPTION_FOR_KEEPING_SANDBOX_DIRECTORY
from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.formatting import emphasis
from exactly_lib.help_texts.test_case.instructions.instruction_names import CHANGE_DIR_INSTRUCTION_NAME
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SUB_DIRECTORY__ACT
from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor, \
    ConstructionEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.textformat_parser import TextParser


class Documentation(SectionContentsConstructor):
    def __init__(self, setup: Setup):
        self.setup = setup

        self._parser = TextParser({
            'phase': setup.phase_names,
            'cwd': emphasis(CHANGE_DIR_INSTRUCTION_NAME),
            'CWD': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
            'act_subdir': SUB_DIRECTORY__ACT,
            'cli_option_for_keeping_sandbox': OPTION_FOR_KEEPING_SANDBOX_DIRECTORY
        })

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        return self._parser.section_contents(_DESCRIPTION)


_DESCRIPTION = """\
Each test case is executed in it's own temporary sandbox directory.
This sandbox is automatically removed after the execution
(unless {cli_option_for_keeping_sandbox} is used).


The sandbox directory contains a sub directory {act_subdir}/, which
is the {CWD} at the start of the test case.


This is the {CWD} for all phases, unless it is changed by the {cwd} instruction.

A change of {CWD} will stay in effect for all following instructions and phases.
"""
