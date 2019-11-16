from exactly_lib.help.entities.configuration_parameters.objects import actor, test_case_status, \
    hds_act_directory, hds_case_directory, timeout


def all_configuration_parameters() -> list:
    """
    :rtype [ConfigurationParameterDocumentation]
    """
    return [
        actor.DOCUMENTATION,
        test_case_status.DOCUMENTATION,
        hds_case_directory.DOCUMENTATION,
        hds_act_directory.DOCUMENTATION,
        timeout.DOCUMENTATION,
    ]
