from exactly_lib.help.entities.concepts.plain_concepts import environment_variable, preprocessor, sandbox, shell_syntax, \
    suite_reporter, symbol, type_, configuration_parameter, current_working_directory


def all_plain_concepts() -> list:
    """
    :rtype [PlainConceptDocumentation]
    """
    return [
        shell_syntax.SHELL_SYNTAX_CONCEPT,
        sandbox.SANDBOX_CONCEPT,
        symbol.SYMBOL_CONCEPT,
        configuration_parameter.CONFIGURATION_PARAMETER_CONCEPT,
        environment_variable.ENVIRONMENT_VARIABLE_CONCEPT,
        preprocessor.PREPROCESSOR_CONCEPT,
        current_working_directory.CURRENT_WORKING_DIRECTORY_CONCEPT,
        suite_reporter.SUITE_REPORTER_CONCEPT,
        type_.TYPE_CONCEPT,
    ]
