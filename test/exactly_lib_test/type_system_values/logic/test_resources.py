from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.lines_transformers import transformers as sut


class FakeLinesTransformer(sut.LinesTransformer):
    def __init__(self):
        pass

    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        raise NotImplementedError('unidentified')
