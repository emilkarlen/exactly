from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.abstract_syntax import env_var_ref_syntax, \
    end_of_1st_var_ref
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import \
    data_restrictions_assertions as asrt_w_str_rend_rest
from exactly_lib_test.type_val_deps.types.string_.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext


class NameWSymRefs:
    RESOLVED_STR = 'the_var_name'
    REF_1 = StringConstantSymbolContext(
        'NAME_SYM_1',
        RESOLVED_STR[:4],
        default_restrictions=asrt_w_str_rend_rest.is__string__w_all_indirect_refs_are_strings(),
    )
    REF_2 = StringConstantSymbolContext(
        'NAME_SYM_2',
        RESOLVED_STR[4:],
        default_restrictions=asrt_w_str_rend_rest.is__string__w_all_indirect_refs_are_strings(),
    )
    SYMBOL_CONTEXTS = (REF_1, REF_2)

    STRING_ABS_STX = str_abs_stx.StringConcatAbsStx([REF_1.abstract_syntax,
                                                     REF_2.abstract_syntax])


class ValueWSymRefsAndVarRefs:
    REFERENCED_VAR_1 = NameAndValue('existing_var_1', '<val of existing 1>')
    REFERENCED_VAR_2 = NameAndValue('existing_var_2', '<val of existing 2>')
    REFERENCED_VAR__ALL = [REFERENCED_VAR_1, REFERENCED_VAR_2]
    VALUE_PATTERN = '{}between{}'
    VALUE_W_VAR_REFS = VALUE_PATTERN.format(
        env_var_ref_syntax(REFERENCED_VAR_1.name),
        env_var_ref_syntax(REFERENCED_VAR_2.name),
    )
    VALUE_WO_VAR_REFS = VALUE_PATTERN.format(
        REFERENCED_VAR_1.value,
        REFERENCED_VAR_2.value,
    )
    POS_OF_END_OF_VAR_REF_1 = end_of_1st_var_ref(VALUE_W_VAR_REFS)
    SYM_REF_PART_1 = StringConstantSymbolContext(
        'VAL_SYM_1',
        VALUE_W_VAR_REFS[:4],
        default_restrictions=asrt_w_str_rend_rest.is__w_str_rendering(),
    )
    CONST_STR_PART_2 = VALUE_W_VAR_REFS[4:(POS_OF_END_OF_VAR_REF_1 + 5)]

    SYM_REF_PART_3 = StringConstantSymbolContext(
        'VAL_SYM_3',
        VALUE_W_VAR_REFS[(POS_OF_END_OF_VAR_REF_1 + 5):],
        default_restrictions=asrt_w_str_rend_rest.is__w_str_rendering(),
    )
    SYMBOL_CONTEXTS = (SYM_REF_PART_1, SYM_REF_PART_3)

    STRING_ABS_STX = str_abs_stx.StringConcatAbsStx([
        SYM_REF_PART_1.abstract_syntax,
        str_abs_stx.StringLiteralAbsStx(CONST_STR_PART_2),
        SYM_REF_PART_3.abstract_syntax,
    ])
