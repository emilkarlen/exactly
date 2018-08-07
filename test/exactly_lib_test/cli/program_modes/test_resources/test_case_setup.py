from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram
from exactly_lib.processing.instruction_setup import InstructionsSetup, TestCaseParsingSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib_test.section_document.test_resources.misc import space_separator_instruction_name_extractor


def test_case_definition_for(instructions_set: InstructionsSetup) -> TestCaseDefinitionForMainProgram:
    return TestCaseDefinitionForMainProgram(
        TestCaseParsingSetup(space_separator_instruction_name_extractor,
                             instructions_set,
                             ActPhaseParser()),
        [])
