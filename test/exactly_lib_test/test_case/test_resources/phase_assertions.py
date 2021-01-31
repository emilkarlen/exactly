from exactly_lib.execution.phase_step import SimplePhaseStep
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def equals_simple_phase_step(expected: SimplePhaseStep) -> Assertion[SimplePhaseStep]:
    assert isinstance(expected, SimplePhaseStep), 'Must be SimplePhaseStep'
    return asrt.and_([
        asrt.sub_component('phase',
                           SimplePhaseStep.phase.fget,
                           asrt.is_(expected.phase)),
        asrt.sub_component('step',
                           SimplePhaseStep.step.fget,
                           asrt.equals(expected.step)),
    ])


def equals_phase(expected: Phase) -> Assertion[Phase]:
    assert isinstance(expected, Phase), 'Must be Phase'
    return asrt.and_([
        asrt.sub_component('the_enum',
                           Phase.the_enum.fget,
                           asrt.equals(expected.the_enum)),
        asrt.sub_component('section_name',
                           Phase.section_name.fget,
                           asrt.equals(expected.section_name)),
        asrt.sub_component('identifier',
                           Phase.identifier.fget,
                           asrt.equals(expected.identifier)),
    ])
