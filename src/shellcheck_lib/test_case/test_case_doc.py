from shellcheck_lib.document.model import PhaseContents, ElementType
from shellcheck_lib.test_case.sections.act import ActPhaseInstruction
from shellcheck_lib.test_case.sections.anonymous import AnonymousPhaseInstruction
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction


class TestCase(tuple):
    def __new__(cls,
                anonymous_phase: PhaseContents,
                setup_phase: PhaseContents,
                act_phase: PhaseContents,
                assert_phase: PhaseContents,
                cleanup_phase: PhaseContents):
        TestCase.__assert_instruction_class(anonymous_phase,
                                            AnonymousPhaseInstruction)
        TestCase.__assert_instruction_class(setup_phase,
                                            SetupPhaseInstruction)
        TestCase.__assert_instruction_class(act_phase,
                                            ActPhaseInstruction)
        TestCase.__assert_instruction_class(assert_phase,
                                            AssertPhaseInstruction)
        TestCase.__assert_instruction_class(cleanup_phase,
                                            CleanupPhaseInstruction)
        return tuple.__new__(cls, (anonymous_phase,
                                   setup_phase,
                                   act_phase,
                                   assert_phase,
                                   cleanup_phase))

    @property
    def anonymous_phase(self) -> PhaseContents:
        return self[0]

    @property
    def setup_phase(self) -> PhaseContents:
        return self[1]

    @property
    def act_phase(self) -> PhaseContents:
        return self[2]

    @property
    def assert_phase(self) -> PhaseContents:
        return self[3]

    @property
    def cleanup_phase(self) -> PhaseContents:
        return self[4]

    @staticmethod
    def __assert_instruction_class(phase_contents: PhaseContents,
                                   instruction_class):
        for element in phase_contents.elements:
            if element.element_type is ElementType.INSTRUCTION:
                assert isinstance(element.instruction, instruction_class)
