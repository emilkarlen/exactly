from exactly_lib.tcfs.path_relativity import SpecificPathRelativity, PathRelativityVariants


def is_satisfied_by(specific_relativity: SpecificPathRelativity,
                    accepted_relativities: PathRelativityVariants) -> bool:
    if specific_relativity.is_absolute:
        return accepted_relativities.absolute
    else:
        return specific_relativity.relativity_type in accepted_relativities.rel_option_types
