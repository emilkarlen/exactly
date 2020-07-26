import unittest

from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType

PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN = PathRelativityVariants({RelOptionType.REL_HDS_ACT,
                                                                   RelOptionType.REL_HDS_CASE,
                                                                   RelOptionType.REL_ACT,
                                                                   RelOptionType.REL_TMP},
                                                                  absolute=True)


def assert_is_list_of_act_phase_instructions(put: unittest.TestCase, x):
    put.assertIsInstance(x, list,
                         'Invalid test input: Expecting list of ActPhaseInstruction:s. Found: ' + str(type(x)))
    i = 0
    for e in x:
        put.assertIsInstance(e, ActPhaseInstruction,
                             'Invalid test input: Element [%d]. Expecting an ActPhaseInstruction:s. Found: %s' %
                             (i, type(e)))
        i += 1
