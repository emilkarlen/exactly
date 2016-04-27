from exactly_lib.document.model import PhaseContents, ElementType
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.anonymous import AnonymousPhaseInstruction
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction


class TestCase(tuple):
    def __new__(cls,
                anonymous_phase: PhaseContents,
                setup_phase: PhaseContents,
                act_phase: PhaseContents,
                before_assert_phase: PhaseContents,
                assert_phase: PhaseContents,
                cleanup_phase: PhaseContents):
        TestCase.__assert_instruction_class(anonymous_phase,
                                            AnonymousPhaseInstruction)
        TestCase.__assert_instruction_class(setup_phase,
                                            SetupPhaseInstruction)
        TestCase.__assert_instruction_class(act_phase,
                                            ActPhaseInstruction)
        TestCase.__assert_instruction_class(before_assert_phase,
                                            BeforeAssertPhaseInstruction)
        TestCase.__assert_instruction_class(assert_phase,
                                            AssertPhaseInstruction)
        TestCase.__assert_instruction_class(cleanup_phase,
                                            CleanupPhaseInstruction)
        return tuple.__new__(cls, (anonymous_phase,
                                   setup_phase,
                                   act_phase,
                                   before_assert_phase,
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
    def before_assert_phase(self) -> PhaseContents:
        return self[3]

    @property
    def assert_phase(self) -> PhaseContents:
        return self[4]

    @property
    def cleanup_phase(self) -> PhaseContents:
        return self[5]

    @staticmethod
    def __assert_instruction_class(phase_contents: PhaseContents,
                                   instruction_class):
        for element in phase_contents.elements:
            if element.element_type is ElementType.INSTRUCTION:
                assert isinstance(element.instruction, instruction_class)
