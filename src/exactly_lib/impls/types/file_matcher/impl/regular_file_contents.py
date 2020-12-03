from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.impls import file_properties
from exactly_lib.impls.types.file_matcher.impl import file_contents_utils, model_constructor_sdv
from exactly_lib.impls.types.file_matcher.impl.model_constructor import ModelConstructor
from exactly_lib.impls.types.string_source.factory import RootStringSourceFactory
from exactly_lib.type_val_deps.types.file_matcher import FileMatcherSdv
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel
from exactly_lib.type_val_prims.string_source.string_source import StringSource

NAMES = file_contents_utils.NamesSetup(
    file_check_properties.REGULAR_FILE_CONTENTS,
    file_properties.FileType.REGULAR,
    syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT,
)


class _ModelConstructor(ModelConstructor[StringSource]):
    def __init__(self, factory: RootStringSourceFactory):
        self._factory = factory

    def make_model(self, model: FileMatcherModel) -> StringSource:
        return self._factory.of_file__described(model.path)


def sdv(contents_matcher: StringMatcherSdv) -> FileMatcherSdv:
    return file_contents_utils.sdv(
        NAMES,
        model_constructor_sdv.with_string_source_construction(_ModelConstructor),
        contents_matcher,
    )
