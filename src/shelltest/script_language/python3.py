from shelltest.script_language import act_script_management
from shelltest.script_language.act_script_management import ScriptFileManager


class Python3Language(act_script_management.ScriptLanguage):
    def command_and_args_for_executing_script_file(self, script_file_name: str) -> list:
        return ['python3', script_file_name]

    def base_name_from_stem(self, stem: str):
        return stem + '.py'

    def comment_line(self, comment: str) -> list:
        return ['# ' + comment]

    def raw_script_statement(self, statement: str) -> list:
        return [statement]


class Python3ScriptFileManager(ScriptFileManager):
    """
    This implementation assumes that the Python 3 interpreter (python3) is in the path.
    """

    def base_name_from_stem(self, stem: str) -> str:
        return stem + '.py'

    def command_and_args_for_executing_script_file(self, script_file_name: str) -> list:
        return ['python3', script_file_name]


def new_script_language_setup() -> act_script_management.ScriptLanguageSetup:
    return act_script_management.ScriptLanguageSetup(
        Python3ScriptFileManager(),
        Python3Language())

