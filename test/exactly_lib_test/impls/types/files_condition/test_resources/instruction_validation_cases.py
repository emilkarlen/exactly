from typing import Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import PrimAndExeExpectation, Arrangement, \
    arrangement_wo_tcds
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.type_val_deps.types.files_condition.test_resources.validation_cases import ValidationCase, \
    failing_validation_cases


def failing_validation_case__multi_exe(case: NameAndValue[ValidationCase]
                                       ) -> NExArr[PrimAndExeExpectation, Arrangement]:
    return NExArr(
        case.name,
        PrimAndExeExpectation.of_exe(
            validation=case.value.expectation,
        ),
        arrangement_wo_tcds(
            symbols=case.value.symbol_table,
        ),
    )


def failing_validation_cases__multi_exe(fc_symbol_name: str = 'files_condition_symbol',
                                        fm_symbol_name: str = 'file_matcher_symbol'
                                        ) -> Sequence[NExArr[PrimAndExeExpectation, Arrangement]]:
    return [
        failing_validation_case__multi_exe(case)
        for case in failing_validation_cases(fc_symbol_name, fm_symbol_name)
    ]
