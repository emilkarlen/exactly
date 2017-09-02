from exactly_lib.help.utils.entity_documentation import EntitiesHelp, EntityDocumentationBase
from exactly_lib.help_texts import entity_names
from exactly_lib.help_texts.entity.builtin import name_and_ref_target


class BuiltinSymbolDocumentation(EntityDocumentationBase):
    def __init__(self, symbol_name: str):
        super().__init__(
            name_and_ref_target(symbol_name, symbol_name)
        )


def builtin_symbols_help(builtin_documentations: iter) -> EntitiesHelp:
    """
    :param builtin_documentations: [BuiltinSymbolDocumentation]
    """
    return EntitiesHelp(entity_names.BUILTIN_ENTITY_TYPE_NAME, builtin_documentations)
