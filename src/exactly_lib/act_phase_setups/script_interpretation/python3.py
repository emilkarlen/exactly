import sys

import exactly_lib.act_phase_setups.script_interpretation.script_language_management
from exactly_lib.act_phase_setups.script_interpretation import script_language_management, standard_script_language
from exactly_lib.act_phase_setups.script_interpretation.script_language_setup import new_for_script_language_setup
from exactly_lib.test_case.phases.act.phase_setup import ActPhaseSetup


def script_language_setup() -> script_language_management.ScriptLanguageSetup:
    return script_language_management.ScriptLanguageSetup(file_manager(),
                                                          language())


def language() -> exactly_lib.act_phase_setups.script_interpretation.script_language_management.ScriptLanguage:
    return standard_script_language.StandardScriptLanguage()


def file_manager() -> script_language_management.ScriptFileManager:
    if not sys.executable:
        raise ValueError('Cannot execute since name of executable not found in sys.executable.')
    return standard_script_language.StandardScriptFileManager('py',
                                                              sys.executable,
                                                              [])


def new_act_phase_setup() -> ActPhaseSetup:
    return new_for_script_language_setup(script_language_setup())
