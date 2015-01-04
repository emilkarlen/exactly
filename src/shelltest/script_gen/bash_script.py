__author__ = 'emil'

from shelltest.exec_abs_syn import script_stmt_gen


class BashShellScriptLanguage(script_stmt_gen.ScriptLanguage):
    def base_name_from_stem(self, name):
        return name + '.sh'

    def raw_script_statement(self, statement: str) -> list:
        return [statement]

    def comment_line(self, comment: str) -> list:
        line = '# ' + comment
        return [line]

    def comment_lines(self, lines: list) -> list:
        return ['# ' + line for line in lines]
