from exactly_lib.cli.custom_symbol import CustomSymbolDocumentation
from exactly_lib.help.entities.builtin.contents_structure import BuiltinSymbolDocumentation
from exactly_lib.symbol.sdv_structure import SymbolDependentValue, SymbolContainer, container_of_builtin
from exactly_lib.symbol.value_type import ValueType


class BuiltinSymbol:
    def __init__(self,
                 name: str,
                 value_type: ValueType,
                 sdv: SymbolDependentValue,
                 documentation: CustomSymbolDocumentation,
                 ):
        self._name = name
        self._value_type = value_type
        self._sdv = sdv
        self._documentation = documentation

    @property
    def name(self) -> str:
        return self._name

    @property
    def container(self) -> SymbolContainer:
        return container_of_builtin(self._value_type, self._sdv)

    @property
    def documentation(self) -> BuiltinSymbolDocumentation:
        return BuiltinSymbolDocumentation(
            self._value_type,
            self.name,
            self._documentation.single_line_description,
            self._documentation.documentation,
            self._documentation.see_also,
        )
