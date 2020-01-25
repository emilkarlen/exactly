import pathlib
import unittest
from typing import Callable, Sequence, List

from exactly_lib.symbol.data import path_sdvs
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel
from exactly_lib.util import symbol_table
from exactly_lib_test.test_case_file_structure.test_resources import tcds_populators
from exactly_lib_test.test_case_file_structure.test_resources.ds_action import \
    MK_DIR_AND_CHANGE_TO_IT_INSIDE_OF_SDS_BUT_OUTSIDE_OF_ANY_OF_THE_RELATIVITY_OPTION_DIRS
from exactly_lib_test.test_case_file_structure.test_resources.ds_construction import TcdsArrangement, \
    tcds_with_act_as_curr_dir_3
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources.assertion import ModelContentsAssertion
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement, DirContents, Dir
from exactly_lib_test.test_resources.test_utils import NEA


def check(put: unittest.TestCase,
          make_model: Callable[[DescribedPath], FilesMatcherModel],
          cases: Sequence[NEA[List[pathlib.Path], List[FileSystemElement]]],
          ):
    relativities = [
        RelOptionType.REL_TMP,
        RelOptionType.REL_ACT,
        RelOptionType.REL_HDS_CASE,
        RelOptionType.REL_CWD,
    ]
    model_name = 'the-model-dir'

    for model_location in relativities:
        model_path_sdv = path_sdvs.of_rel_option_with_const_file_name(model_location, model_name)
        for case in cases:
            with put.subTest(case.name,
                             relativity=model_location):
                tcds_contents = TcdsArrangement(
                    pre_population_action=
                    MK_DIR_AND_CHANGE_TO_IT_INSIDE_OF_SDS_BUT_OUTSIDE_OF_ANY_OF_THE_RELATIVITY_OPTION_DIRS,
                    tcds_contents=tcds_populators.TcdsPopulatorForRelOptionType(
                        model_location,
                        DirContents([Dir(model_name, case.actual)]),
                    ),
                )
                with tcds_with_act_as_curr_dir_3(tcds_contents) as tcds:
                    model_path = model_path_sdv.resolve(SYMBOLS).value_of_any_dependency__d(tcds)

                    # ACT #

                    actual = make_model(model_path)

                    # ASSERT #

                    expectation = ModelContentsAssertion(model_path.primitive,
                                                         case.expected)

                    expectation.apply_without_message(put, actual)


SYMBOLS = symbol_table.empty_symbol_table()
