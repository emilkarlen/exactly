from exactly_lib.instructions.utils.arg_parse.relative_path_options import RelOptionType


class RelOptionsConfiguration(tuple):
    def __new__(cls,
                accepted_options: iter,
                default_option: RelOptionType):
        """
        :type accepted_options: Iterable of `RelOptionType`
        """
        return tuple.__new__(cls, (accepted_options,
                                   default_option))

    @property
    def accepted_options(self) -> iter:
        """
        :rtype: Iterable of `RelOptionType`
        """
        return self[0]

    @property
    def default_option(self) -> RelOptionType:
        return self[1]


class RelOptionArgumentConfiguration(tuple):
    def __new__(cls,
                options_configuration: RelOptionsConfiguration,
                argument_syntax_name: str):
        return tuple.__new__(cls, (options_configuration,
                                   argument_syntax_name))

    @property
    def options(self) -> RelOptionsConfiguration:
        return self[0]

    @property
    def argument_syntax_name(self) -> str:
        return self[1]


def argument_configuration_for_file_creation(argument_syntax_element_name: str) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(OPTIONS_FOR_FILE_CREATION, argument_syntax_element_name)


OPTIONS_FOR_FILE_CREATION = RelOptionsConfiguration([RelOptionType.REL_ACT,
                                                     RelOptionType.REL_TMP],
                                                    RelOptionType.REL_CWD)
