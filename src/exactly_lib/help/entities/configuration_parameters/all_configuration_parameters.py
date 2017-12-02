from exactly_lib.help.entities.configuration_parameters.objects import actor, test_case_status, \
    home_act_directory, home_case_directory, timeout


def all_configuration_parameters() -> list:
    """
    :rtype [ConfigurationParameterDocumentation]
    """
    return [
        actor.DOCUMENTATION,
        test_case_status.DOCUMENTATION,
        home_case_directory.DOCUMENTATION,
        home_act_directory.DOCUMENTATION,
        timeout.DOCUMENTATION,
    ]
