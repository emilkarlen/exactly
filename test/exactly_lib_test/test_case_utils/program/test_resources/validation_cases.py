from exactly_lib.symbol.data import string_sdvs
from exactly_lib.test_case_utils.string_transformer.sdvs import StringTransformerSdvReference
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Arrangement, arrangement_wo_tcds, \
    PrimAndExeExpectation
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.string_transformers.test_resources import \
    validation_cases as str_trans_validation_cases
from exactly_lib_test.test_resources.test_utils import NExArr


def validation_exe_case(validation_case: NameAndValue[str_trans_validation_cases.ValidationCase],
                        program_symbol_name: str,
                        ) -> NExArr[PrimAndExeExpectation, Arrangement]:
    program_w_transformer = program_sdvs.system_program(
        string_sdvs.str_constant('system-program')
    ).new_with_appended_transformations([
        StringTransformerSdvReference(validation_case.value.symbol_context.name)
    ])

    program_symbol = ProgramSymbolContext.of_sdv(
        program_symbol_name,
        program_w_transformer
    )
    return NExArr(
        validation_case.name,
        PrimAndExeExpectation.of_exe(
            validation=validation_case.value.expectation,
        ),
        arrangement_wo_tcds(
            symbols=SymbolContext.symbol_table_of_contexts([
                program_symbol,
                validation_case.value.symbol_context,
            ]),
        )
    )
