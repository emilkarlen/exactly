from shellcheck_lib.act_phase_setups import python3
from shellcheck_lib.act_phase_setups import single_command_setup
from shellcheck_lib.act_phase_setups.script_language_setup import new_for_script_language_setup
from shellcheck_lib.script_language import standard_script_language
from shellcheck_lib.script_language.script_language_management import ScriptLanguageSetup
from shellcheck_lib.test_case.phases.act.phase_setup import ActPhaseSetup

INTERPRETER_FOR_TEST = 'test-language'


def resolve_act_phase_setup_from_argparse_argument(interpreter: list) -> ActPhaseSetup:
    interpreter_argument = None
    if interpreter and len(interpreter) > 0:
        interpreter_argument = interpreter[0]
    return resolve_act_phase_setup(interpreter_argument)


def resolve_act_phase_setup(interpreter: str=None) -> ActPhaseSetup:
    if interpreter:
        if interpreter == INTERPRETER_FOR_TEST:
            return python3.new_act_phase_setup()
        else:
            return new_for_generic_script_language_setup(interpreter)
    return single_command_setup.act_phase_setup()


def new_for_generic_script_language_setup(interpreter: str) -> ActPhaseSetup:
    return new_for_script_language_setup(
        ScriptLanguageSetup(
            standard_script_language.StandardScriptFileManager('src',
                                                               interpreter,
                                                               []),
            standard_script_language.StandardScriptLanguage))
