__author__ = 'emil'


def string_expr(value: str) -> str:
    return '\'' + value.replace('\'', '\\\'') + '\''


def print_value(value_expr: str,
                output_file_variable=None) -> str:
    file_expr = ''
    if output_file_variable:
        file_expr = ', file=' + output_file_variable
    return 'print(' + value_expr + file_expr + ')'


def print_header_value(header_expr: str,
                       value_expr: str,
                       output_file_variable=None) -> str:
    file_expr = ''
    if output_file_variable:
        file_expr = ', file=' + output_file_variable
    return 'print(' + string_expr('%-30s: %s') + ' % (' + header_expr + ',' + value_expr + ')' + file_expr + ')'


def with_opened_file(file_name: str, file_var: str, mode: str, statements: list) -> list:
    open_stmt = 'with open(%s,%s) as %s:' % (string_expr(file_name), string_expr(mode), file_var)
    indented_statements = ['  ' + stmt for stmt in statements]
    indented_statements.insert(0, open_stmt)
    return indented_statements


def env_var_expr(env_var_name: str) -> str:
    return 'os.environ[%s]' % string_expr(env_var_name)

def program_lines(used_modules: set,
                  statements: list) -> list:
    ret_val = []
    for module in used_modules:
        ret_val.append('import ' + module)
    ret_val.append('')
    ret_val.extend(statements)
    return ret_val