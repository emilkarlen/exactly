from shellcheck_lib.script_language import python3
from shellcheck_lib.script_language.act_script_management import ScriptLanguageSetup


def resolve_script_language(interpreter: str=None) -> ScriptLanguageSetup:
    if interpreter and interpreter == INTERPRETER_FOR_TEST:
        return python3.new_script_language_setup()
    return python3.new_script_language_setup()


INTERPRETER_FOR_TEST = 'test-language'
