from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.described_dep_val import sdv_of_constant_primitive
from exactly_lib.test_case_utils.file_matcher.impl import file_contents_utils
from exactly_lib.test_case_utils.string_transformer.impl import identity
from exactly_lib.type_system.logic import string_matcher
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, FileMatcherSdv
from exactly_lib.type_system.logic.string_matcher import FileToCheck, StringMatcherSdv

NAMES = file_contents_utils.NamesSetup(
    file_check_properties.REGULAR_FILE_CONTENTS,
    file_properties.FileType.REGULAR,
    syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT,
)


class _ModelConstructor(file_contents_utils.ModelConstructor[FileToCheck]):
    def make_model(self, model: FileMatcherModel) -> FileToCheck:
        return string_matcher.FileToCheck(
            model.path,
            identity.IdentityStringTransformer(),
            string_matcher.DestinationFilePathGetter(),
        )


def sdv(contents_matcher: StringMatcherSdv) -> FileMatcherSdv:
    return file_contents_utils.sdv(
        NAMES,
        sdv_of_constant_primitive(_ModelConstructor()),
        contents_matcher,
    )
