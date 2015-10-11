import sys

from shellcheck_lib.execution.partial_execution import ScriptHandling
from shellcheck_lib.script_language import script_language_management
from shellcheck_lib.act_phase_setups.script_language_setup import ActScriptExecutorForScriptLanguage
from shellcheck_lib.test_case.sections.act import script_source


class Python3Language(script_source.ScriptLanguage):
    def comment_line(self, comment: str) -> list:
        return ['# ' + comment]

    def raw_script_statement(self, statement: str) -> list:
        return [statement]


class Python3ScriptFileManager(script_language_management.ScriptFileManager):
    """
    This implementation assumes that the Python 3 interpreter (python3) is in the path.
    """

    def __init__(self):
        if not sys.executable:
            raise ValueError('Cannot execute test since name of executable not found in sys.executable.')
        self.__interpreter = sys.executable

    def base_name_from_stem(self, stem: str) -> str:
        return stem + '.py'

    def command_and_args_for_executing_script_file(self, script_file_name: str) -> list:
        return [self.__interpreter, script_file_name]


def new_script_language_setup() -> script_language_management.ScriptLanguageSetup:
    return script_language_management.ScriptLanguageSetup(
        Python3ScriptFileManager(),
        Python3Language())


def new_script_handling() -> ScriptHandling:
    script_language_setup = new_script_language_setup()
    return ScriptHandling(script_language_setup.new_builder(),
                          ActScriptExecutorForScriptLanguage(script_language_setup))
