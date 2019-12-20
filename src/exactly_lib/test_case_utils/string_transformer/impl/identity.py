from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerModel


class IdentityStringTransformer(StringTransformer):
    @property
    def name(self) -> str:
        return 'identity'

    @property
    def is_identity_transformer(self) -> bool:
        return True

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return lines
