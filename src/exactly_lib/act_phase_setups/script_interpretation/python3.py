import sys

import exactly_lib.act_phase_setups.script_interpretation.script_language_management
from exactly_lib.act_phase_setups.script_interpretation import script_language_management
from exactly_lib.act_phase_setups.script_interpretation.script_language_management import ScriptLanguage
from exactly_lib.act_phase_setups.script_interpretation.script_language_setup import new_for_script_language_setup
from exactly_lib.test_case.phases.act.phase_setup import ActPhaseSetup


def script_language_setup() -> script_language_management.ScriptLanguageSetup:
    return script_language_management.ScriptLanguageSetup(file_manager(),
                                                          language())


def language() -> ScriptLanguage:
    return PythonScriptLanguage()


def file_manager() -> script_language_management.ScriptFileManager:
    if not sys.executable:
        raise ValueError('Cannot execute since name of executable not found in sys.executable.')
    return exactly_lib.act_phase_setups.script_interpretation.script_language_management.StandardScriptFileManager('py',
                                                                                                                   sys.executable,
                                                                                                                   [])


def new_act_phase_setup() -> ActPhaseSetup:
    return new_for_script_language_setup(script_language_setup())


class PythonScriptLanguage(ScriptLanguage):
    def comment_line(self, comment: str) -> list:
        return ['# ' + comment]

    def raw_script_statement(self, statement: str) -> list:
        return [statement]
