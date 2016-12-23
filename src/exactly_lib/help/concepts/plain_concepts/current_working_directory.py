from exactly_lib import program_info
from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import OPTION_FOR_PREPROCESSOR
from exactly_lib.default.program_modes.test_case.default_instruction_names import CHANGE_DIR_INSTRUCTION_NAME
from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation
from exactly_lib.help.concepts.names_and_cross_references import CURRENT_WORKING_DIRECTORY_CONCEPT_INFO
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.formatting import InstructionName
from exactly_lib.help.utils.phase_names import phase_name_dictionary
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.test_case.sandbox_directory_structure import SUB_DIRECTORY__ACT
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.structure.structures import text


class _CurrentWorkingDirectoryConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(CURRENT_WORKING_DIRECTORY_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        tp = TextParser({
            'preprocessor_option': formatting.cli_option(OPTION_FOR_PREPROCESSOR),
            'phase': phase_name_dictionary(),
            'act_dir': SUB_DIRECTORY__ACT,
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'cd_instruction': InstructionName(CHANGE_DIR_INSTRUCTION_NAME),
            'sandbox': formatting.concept(SANDBOX_CONCEPT.name().singular),
            'concept': formatting.concept(self.name().singular),
        })
        return from_simple_description(
            Description(text(_SINGLE_LINE_DESCRIPTION),
                        tp.fnap(_DESCRIPTION_REST)))


CURRENT_WORKING_DIRECTORY_CONCEPT = _CurrentWorkingDirectoryConcept()

_SINGLE_LINE_DESCRIPTION = """\
The current directory of the environment in which an instruction is executed."""

_DESCRIPTION_REST = """\
The {phase[setup]} phase, and all following phases, has a {concept},
just like a normal program does.


The {concept} is also the {concept} for the {program_name} process, so that external programs
and shell commands have the same {concept} as instructions.


At the beginning, the {concept} is the {act_dir}/ subdirectory of the {sandbox}.


It can be changed using the {cd_instruction} instruction.


The {concept} at the end of one phase becomes
the {concept} at the beginning of the following phase.
"""
