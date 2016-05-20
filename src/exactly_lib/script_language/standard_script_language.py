import exactly_lib.script_language.script_language_management
from exactly_lib.script_language.script_language_management import ScriptFileManager


class StandardScriptFileManager(ScriptFileManager):
    def __init__(self,
                 extension_after_dot: str,
                 interpreter: str,
                 command_line_options_before_file_argument: list):
        self.extension_after_dot = extension_after_dot
        self.interpreter = interpreter
        self.command_line_options_before_file_argument = command_line_options_before_file_argument

    def base_name_from_stem(self, stem: str) -> str:
        return stem + '.' + self.extension_after_dot

    def command_and_args_for_executing_script_file(self, script_file_name: str) -> list:
        return [self.interpreter] + self.command_line_options_before_file_argument + [script_file_name]


class StandardScriptLanguage(exactly_lib.script_language.script_language_management.ScriptLanguage):
    def comment_line(self, comment: str) -> list:
        return ['# ' + comment]

    def raw_script_statement(self, statement: str) -> list:
        return [statement]
