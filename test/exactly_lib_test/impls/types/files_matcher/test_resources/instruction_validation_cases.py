from typing import Sequence

from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import PrimAndExeExpectation, Arrangement, \
    arrangement_wo_tcds
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.type_val_deps.types.files_matcher.test_resources.validation_cases import failing_validation_cases


def failing_validation_cases__multi_exe(symbol_name: str = 'files_matcher_symbol'
                                        ) -> Sequence[NExArr[PrimAndExeExpectation, Arrangement]]:
    return [
        NExArr(
            case.name,
            PrimAndExeExpectation.of_exe(
                validation=case.value.expectation,
            ),
            arrangement_wo_tcds(
                symbols=case.value.symbol_context.symbol_table,
            ),
        )
        for case in failing_validation_cases(symbol_name)
    ]
