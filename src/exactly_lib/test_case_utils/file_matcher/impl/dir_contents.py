from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher.impl import file_contents_utils
from exactly_lib.test_case_utils.files_matcher.new_model_impl import FilesMatcherModelForDir
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, FileMatcherSdvType
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcherSdvType


class _Setup(file_contents_utils.Setup[FilesMatcherModel]):
    def __init__(self):
        super().__init__(
            file_check_properties.DIR_CONTENTS,
            file_properties.FileType.DIRECTORY,
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT,
        )

    def make_model(self, model: FileMatcherModel) -> FilesMatcherModel:
        return FilesMatcherModelForDir(
            model.path,
            None,
        )


SETUP = _Setup()


def dir_matches_files_matcher_sdv__generic(contents_matcher: FilesMatcherSdvType) -> FileMatcherSdvType:
    return file_contents_utils.sdv__generic(
        SETUP,
        contents_matcher,
    )
