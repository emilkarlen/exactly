from typing import Sequence, Tuple

from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram
from exactly_lib.default import instruction_name_and_argument_splitter
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup, InstructionsSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.util.string import lines_content
from exactly_lib_test.common.test_resources.instruction_setup import single_instruction_setup


def test_case_definition_with_only_assert_phase_instructions(
        assert_phase_instructions: Sequence[Tuple[str, AssertPhaseInstruction]]
) -> TestCaseDefinitionForMainProgram:
    assert_phase_instructions_dict = {
        name: single_instruction_setup(name, instruction)
        for name, instruction in assert_phase_instructions
    }
    return TestCaseDefinitionForMainProgram(
        TestCaseParsingSetup(
            instruction_name_extractor_function=instruction_name_and_argument_splitter.splitter,
            instruction_setup=InstructionsSetup(
                config_instruction_set={},
                setup_instruction_set={},
                assert_instruction_set=assert_phase_instructions_dict,
                before_assert_instruction_set={},
                cleanup_instruction_set={},
            ),
            act_phase_parser=ActPhaseParser()),
        builtin_symbols=[]
    )


def test_case_source_with_single_act_phase_instruction(instruction: str) -> str:
    return lines_content([
        phase_names.ACT.syntax,
        instruction,
    ])
