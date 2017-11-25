from exactly_lib import program_info
from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import OPTION_FOR_PREPROCESSOR
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.formatting import InstructionName
from exactly_lib.help_texts.test_case.instructions.instruction_names import CHANGE_DIR_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import PHASE_NAME_DICTIONARY
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SUB_DIRECTORY__ACT
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.textformat_parser import TextParser


class _CurrentWorkingDirectoryConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        tp = TextParser({
            'preprocessor_option': formatting.cli_option(OPTION_FOR_PREPROCESSOR),
            'phase': PHASE_NAME_DICTIONARY,
            'act_dir': SUB_DIRECTORY__ACT,
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'cd_instruction': InstructionName(CHANGE_DIR_INSTRUCTION_NAME),
            'sandbox': formatting.concept_(concepts.SANDBOX_CONCEPT_INFO),
            'concept': formatting.concept(self.singular_name()),
        })
        return from_simple_description(
            Description(self.single_line_description(),
                        tp.fnap(_DESCRIPTION_REST)))


CURRENT_WORKING_DIRECTORY_CONCEPT = _CurrentWorkingDirectoryConcept()

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
