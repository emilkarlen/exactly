from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType


class RelOptionsConfiguration(tuple):
    def __new__(cls,
                accepted_relativity_variants: PathRelativityVariants,
                default_option: RelOptionType):
        """
        :type accepted_options: Iterable of `RelOptionType`
        """
        return tuple.__new__(cls, (accepted_relativity_variants,
                                   default_option))

    @property
    def accepted_relativity_variants(self) -> PathRelativityVariants:
        return self[0]

    @property
    def accepted_options(self) -> iter:
        """
        :rtype: Iterable of `RelOptionType`
        """
        return self.accepted_relativity_variants.rel_option_types

    @property
    def default_option(self) -> RelOptionType:
        return self[1]


class RelOptionArgumentConfiguration(tuple):
    def __new__(cls,
                options_configuration: RelOptionsConfiguration,
                argument_syntax_name: str,
                path_suffix_is_required: bool):
        return tuple.__new__(cls, (options_configuration,
                                   argument_syntax_name,
                                   path_suffix_is_required))

    @property
    def options(self) -> RelOptionsConfiguration:
        return self[0]

    @property
    def path_suffix_is_required(self) -> bool:
        return self[2]

    @property
    def argument_syntax_name(self) -> str:
        return self[1]


RELATIVITY_VARIANTS_FOR_FILE_CREATION = PathRelativityVariants({RelOptionType.REL_ACT,
                                                                RelOptionType.REL_TMP,
                                                                RelOptionType.REL_CWD},
                                                               False)

REL_OPTIONS_FOR_FILE_CREATION = RelOptionsConfiguration(RELATIVITY_VARIANTS_FOR_FILE_CREATION,
                                                        RelOptionType.REL_CWD)


def argument_configuration_for_file_creation(argument_syntax_element_name: str) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(REL_OPTIONS_FOR_FILE_CREATION,
                                          argument_syntax_element_name,
                                          True)


RELATIVITY_VARIANTS_FOR_SOURCE_FILES__PRE_ACT = PathRelativityVariants({RelOptionType.REL_HOME_CASE,
                                                                        RelOptionType.REL_HOME_ACT,
                                                                        RelOptionType.REL_ACT,
                                                                        RelOptionType.REL_TMP,
                                                                        RelOptionType.REL_CWD},
                                                                       True)

REL_OPTIONS_FOR_SOURCE_FILES__PRE_ACT = RelOptionsConfiguration(RELATIVITY_VARIANTS_FOR_SOURCE_FILES__PRE_ACT,
                                                                RelOptionType.REL_CWD)


def argument_configuration_for_source_file__pre_act(
        argument_syntax_element_name: str) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(
        REL_OPTIONS_FOR_SOURCE_FILES__PRE_ACT,
        argument_syntax_element_name,
        True)


RELATIVITY_VARIANTS_FOR_SOURCE_FILES__POST_ACT = PathRelativityVariants({RelOptionType.REL_HOME_CASE,
                                                                         RelOptionType.REL_HOME_ACT,
                                                                         RelOptionType.REL_ACT,
                                                                         RelOptionType.REL_TMP,
                                                                         RelOptionType.REL_CWD,
                                                                         RelOptionType.REL_RESULT},
                                                                        True)

REL_OPTIONS_FOR_SOURCE_FILES__POST_ACT = RelOptionsConfiguration(RELATIVITY_VARIANTS_FOR_SOURCE_FILES__POST_ACT,
                                                                 RelOptionType.REL_CWD)


def argument_configuration_for_source_file__post_act(
        argument_syntax_element_name: str) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(
        REL_OPTIONS_FOR_SOURCE_FILES__POST_ACT,
        argument_syntax_element_name,
        True)
