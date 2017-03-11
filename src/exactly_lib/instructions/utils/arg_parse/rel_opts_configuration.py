from exactly_lib.instructions.utils.relativity_root import RelOptionType
from exactly_lib.test_case.file_ref_relativity import PathRelativityVariants


class RelOptionsConfiguration(tuple):
    def __new__(cls,
                accepted_options: iter,
                is_rel_val_def_option_accepted: bool,
                default_option: RelOptionType):
        """
        :type accepted_options: Iterable of `RelOptionType`
        """
        return tuple.__new__(cls, (accepted_options,
                                   is_rel_val_def_option_accepted,
                                   default_option))

    @property
    def accepted_options(self) -> iter:
        """
        :rtype: Iterable of `RelOptionType`
        """
        return self[0]

    @property
    def is_rel_val_def_option_accepted(self) -> bool:
        """
        Tells if the option for relativity of a value definition is accepted.
        """
        return self[1]

    @property
    def default_option(self) -> RelOptionType:
        return self[2]


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


RELATIVITY_VARIANTS_FOR_FILE_CREATION = PathRelativityVariants({RelOptionType.REL_ACT,
                                                                RelOptionType.REL_TMP,
                                                                RelOptionType.REL_CWD},
                                                               False)

OPTIONS_FOR_FILE_CREATION = RelOptionsConfiguration(RELATIVITY_VARIANTS_FOR_FILE_CREATION.rel_option_types,
                                                    True,
                                                    RelOptionType.REL_CWD)
