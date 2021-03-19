from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions.test_case.instructions import define_symbol as help_texts
from exactly_lib.symbol.err_msg.error_messages import invalid_type_msg
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.symbol.value_type import WithStrRenderingType, ValueType
from exactly_lib.tcfs.path_relativity import PathRelativityVariants
from exactly_lib.type_val_deps.sym_ref.restrictions import WithStrRenderingTypeRestrictions
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import OrReferenceRestrictions, \
    OrRestrictionPart, ReferenceRestrictionsOnDirectAndIndirect, is_string__all_indirect_refs_are_strings
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import PathAndRelativityRestriction
from exactly_lib.util.str_ import str_constructor


def path_or_string_reference_restrictions(
        accepted_relativity_variants: PathRelativityVariants) -> WithStrRenderingTypeRestrictions:
    return OrReferenceRestrictions([
        OrRestrictionPart(
            WithStrRenderingType.PATH,
            path_relativity_restriction(accepted_relativity_variants)),
        OrRestrictionPart(
            WithStrRenderingType.STRING,
            PATH_COMPONENT_STRING_REFERENCES_RESTRICTION),
    ],
        type_must_be_either_path_or_string__err_msg_generator
    )


def path_relativity_restriction(accepted_relativity_variants: PathRelativityVariants):
    return ReferenceRestrictionsOnDirectAndIndirect(
        PathAndRelativityRestriction(accepted_relativity_variants))


PATH_COMPONENT_STRING_REFERENCES_RESTRICTION = is_string__all_indirect_refs_are_strings(
    text_docs.single_pre_formatted_line_object(
        str_constructor.FormatMap(
            'Every symbol used as a path component of a {path_type} '
            'must be defined as a {string_type}.',
            {
                'path_type': help_texts.TYPE_W_STR_RENDERING_INFO_DICT[WithStrRenderingType.PATH].identifier,
                'string_type': help_texts.TYPE_W_STR_RENDERING_INFO_DICT[WithStrRenderingType.STRING].identifier,
            },
        )
    )
)


def type_must_be_either_path_or_string__err_msg_generator(name_of_failing_symbol: str,
                                                          container_of_illegal_symbol: SymbolContainer) -> TextRenderer:
    return invalid_type_msg([ValueType.PATH, ValueType.STRING],
                            name_of_failing_symbol,
                            container_of_illegal_symbol)
