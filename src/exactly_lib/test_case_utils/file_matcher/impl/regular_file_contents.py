from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher.impl import file_contents_utils, model_constructor_sdv
from exactly_lib.test_case_utils.file_matcher.impl.model_constructor import ModelConstructor
from exactly_lib.test_case_utils.string_models.factory import StringModelFactory
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, FileMatcherSdv
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv
from exactly_lib.type_system.logic.string_model import StringModel

NAMES = file_contents_utils.NamesSetup(
    file_check_properties.REGULAR_FILE_CONTENTS,
    file_properties.FileType.REGULAR,
    syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT,
)


class _ModelConstructor(ModelConstructor[StringModel]):
    def __init__(self, factory: StringModelFactory):
        self._factory = factory

    def make_model(self, model: FileMatcherModel) -> StringModel:
        return self._factory.of_file(model.path.primitive)


def sdv(contents_matcher: StringMatcherSdv) -> FileMatcherSdv:
    return file_contents_utils.sdv(
        NAMES,
        model_constructor_sdv.with_string_model_construction(_ModelConstructor),
        contents_matcher,
    )
