from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType

PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN = PathRelativityVariants({RelOptionType.REL_HOME_ACT,
                                                                   RelOptionType.REL_HOME_CASE,
                                                                   RelOptionType.REL_ACT,
                                                                   RelOptionType.REL_TMP},
                                                                  absolute=True)