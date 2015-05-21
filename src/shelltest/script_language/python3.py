from shelltest.test_case import script_stmt_gen
from shelltest.test_case.script_stmt_gen import ScriptFileManager


class Python3Language(script_stmt_gen.ScriptLanguage):
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


def new_script_language_setup() -> script_stmt_gen.ScriptLanguageSetup:
    return script_stmt_gen.ScriptLanguageSetup(
        Python3ScriptFileManager(),
        Python3Language())

