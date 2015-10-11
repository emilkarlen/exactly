from shellcheck_lib.execution.partial_execution import ScriptHandling
from shellcheck_lib.act_phase_setups.script_language_setup import ActScriptExecutorForScriptLanguage
from shellcheck_lib.script_language import python3 as python3_language
from shellcheck_lib.act_phase_setups.script_language_setup import new_for_script_language_setup
from shellcheck_lib.test_case.sections.act.phase_setup import ActPhaseSetup


def new_act_phase_setup() -> ActPhaseSetup:
    return new_for_script_language_setup(python3_language.script_language_setup())


def new_script_handling() -> ScriptHandling:
    script_language_setup = python3_language.script_language_setup()
    return ScriptHandling(script_language_setup.new_builder(),
                          ActScriptExecutorForScriptLanguage(script_language_setup))
