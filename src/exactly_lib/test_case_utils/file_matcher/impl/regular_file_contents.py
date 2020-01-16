from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher.impl import file_contents_utils
from exactly_lib.test_case_utils.string_transformer.impl import identity
from exactly_lib.type_system.logic import string_matcher
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, FileMatcherSdvType
from exactly_lib.type_system.logic.string_matcher import FileToCheck, GenericStringMatcherSdv


class _Setup(file_contents_utils.Setup[FileToCheck]):
    def __init__(self):
        super().__init__(
            file_check_properties.REGULAR_FILE_CONTENTS,
            file_properties.FileType.REGULAR,
            syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT,
        )

    def make_model(self, model: FileMatcherModel) -> FileToCheck:
        return string_matcher.FileToCheck(
            model.path,
            identity.IdentityStringTransformer(),
            string_matcher.DestinationFilePathGetter(),
        )


SETUP = _Setup()


def sdv__generic(contents_matcher: GenericStringMatcherSdv) -> FileMatcherSdvType:
    return file_contents_utils.sdv__generic(
        SETUP,
        contents_matcher,
    )
