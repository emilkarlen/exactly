from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.lines_transformer.transformers import CustomLinesTransformer


class ToUpperCaseLinesTransformer(CustomLinesTransformer):
    @property
    def is_identity_transformer(self) -> bool:
        return False

    def transform(self,
                  tcds: HomeAndSds,
                  lines: iter) -> iter:
        return map(str.upper, lines)


class ToLowerCaseLinesTransformer(CustomLinesTransformer):
    @property
    def is_identity_transformer(self) -> bool:
        return False

    def transform(self,
                  tcds: HomeAndSds,
                  lines: iter) -> iter:
        return map(str.lower, lines)
