from exactly_lib.test_case_file_structure.path_relativity import SpecificPathRelativity, PathRelativityVariants
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP


def is_satisfied_by(specific_relativity: SpecificPathRelativity,
                    accepted_relativities: PathRelativityVariants) -> str:
    if specific_relativity.is_absolute:
        if accepted_relativities.absolute:
            return None
        else:
            return 'An absolute path is not allowed'
    else:
        if specific_relativity.relativity_type in accepted_relativities.rel_option_types:
            return None
        else:
            return 'A path that is relative {} is not allowed'.format(
                REL_OPTIONS_MAP[specific_relativity.relativity_type].description
            )
