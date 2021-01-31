from exactly_lib.definitions import instruction_arguments
from exactly_lib.impls.instructions import source_file_relativities
from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionsConfiguration
from exactly_lib.tcfs.path_relativity import RelOptionType

CONTENTS_ASSIGNMENT_TOKEN = instruction_arguments.ASSIGNMENT_OPERATOR


def src_rel_opt_arg_conf_for_phase(phase_is_after_act: bool,
                                   ) -> RelOptionsConfiguration:
    return source_file_relativities.src_rel_opt_conf_for_phase(RelOptionType.REL_HDS_CASE,
                                                               phase_is_after_act)
