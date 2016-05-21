from exactly_lib.act_phase_setups.script_interpretation.script_language_management import ScriptLanguage


class StandardScriptLanguage(ScriptLanguage):
    def comment_line(self, comment: str) -> list:
        return []

    def raw_script_statement(self, statement: str) -> list:
        return [statement]
