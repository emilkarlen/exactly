from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer


class ToUppercaseLinesTransformer(LinesTransformer):
    def transform(self,
                  tcds: HomeAndSds,
                  lines: iter) -> iter:
        return map(str.upper, lines)


class TransformedContentsSetupWithDependenceOnHomeAndSds:
    def __init__(self,
                 original: str,
                 transformed: str):
        self.original = original
        self.transformed = transformed

    def contents_before_replacement(self, home_and_sds: HomeAndSds) -> str:
        return self.original

    def expected_contents_after_replacement(self, home_and_sds: HomeAndSds) -> str:
        return self.transformed


class TransformedContentsSetup:
    def __init__(self,
                 original: str,
                 transformed: str):
        self.original = original
        self.transformed = transformed
