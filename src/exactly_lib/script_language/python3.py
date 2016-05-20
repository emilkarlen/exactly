import sys

import exactly_lib.script_language.script_language_management
from . import script_language_management
from . import standard_script_language


def script_language_setup() -> script_language_management.ScriptLanguageSetup:
    return script_language_management.ScriptLanguageSetup(file_manager(),
                                                          language())


def language() -> exactly_lib.script_language.script_language_management.ScriptLanguage:
    return standard_script_language.StandardScriptLanguage()


def file_manager() -> script_language_management.ScriptFileManager:
    if not sys.executable:
        raise ValueError('Cannot execute test since name of executable not found in sys.executable.')
    return standard_script_language.StandardScriptFileManager('py',
                                                              sys.executable,
                                                              [])
