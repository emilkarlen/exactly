import pathlib
import types

from exactly_lib_test.execution.test_resources import python_code_gen as py


def print_to_file__generate_script(code_using_file_opened_for_writing: types.FunctionType,
                                   file_name: str):
    """
    Function that is designed as the execution__generate_script argument to TestCaseSetup, after
    giving the first two arguments using partial application.

    :param code_using_file_opened_for_writing: function: file_variable: str -> ModulesAndStatements
    :param file_name: the name of the file to output to.
    :param global_environment: Environment from act instruction
    :param phase_environment: Environment from act instruction
    """
    file_path = pathlib.Path() / file_name
    file_name = str(file_path)
    file_var = '_file_var'
    mas = code_using_file_opened_for_writing(file_var)
    all_statements = py.with_opened_file(file_name,
                                         file_var,
                                         'w',
                                         mas.statements)

    return py.program_lines(mas.used_modules,
                            all_statements)
