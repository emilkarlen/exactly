from shellcheck_lib.script_language import python3
from shellcheck_lib.act_phase_setups.script_language_setup import new_for_script_language_setup
from shellcheck_lib.test_case.sections.act.phase_setup import ActPhaseSetup


def resolve_act_phase_setup(interpreter: str=None) -> ActPhaseSetup:
    if interpreter and interpreter == INTERPRETER_FOR_TEST:
        return _py3_setup()
    return _py3_setup()


def _py3_setup() -> ActPhaseSetup:
    return new_for_script_language_setup(python3.new_script_language_setup())


INTERPRETER_FOR_TEST = 'test-language'
