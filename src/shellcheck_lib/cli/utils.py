from shellcheck_lib.act_phase_setups import python3
from shellcheck_lib.test_case.sections.act.phase_setup import ActPhaseSetup


def resolve_act_phase_setup(interpreter: str=None) -> ActPhaseSetup:
    if interpreter and interpreter == INTERPRETER_FOR_TEST:
        return python3.new_act_phase_setup()
    return python3.new_act_phase_setup()


INTERPRETER_FOR_TEST = 'test-language'
