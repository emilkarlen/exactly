from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher.impl import file_contents_utils
from exactly_lib.test_case_utils.files_matcher import models
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, GenericFileMatcherSdv
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, GenericFilesMatcherSdv
from exactly_lib.util.cli_syntax import option_syntax


class _SetupNonRecursive(file_contents_utils.Setup[FilesMatcherModel]):
    def __init__(self):
        super().__init__(
            file_check_properties.DIR_CONTENTS,
            file_properties.FileType.DIRECTORY,
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT,
        )

    def make_model(self, model: FileMatcherModel) -> FilesMatcherModel:
        return models.non_recursive(model.path)


SETUP__NON_RECURSIVE = _SetupNonRecursive()


class _SetupRecursive(file_contents_utils.Setup[FilesMatcherModel]):
    def __init__(self):
        super().__init__(
            ' '.join((file_check_properties.DIR_CONTENTS,
                      option_syntax.option_syntax(instruction_arguments.RECURSIVE_OPTION.name))),
            file_properties.FileType.DIRECTORY,
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT,
        )

    def make_model(self, model: FileMatcherModel) -> FilesMatcherModel:
        return models.recursive(model.path)


SETUP__RECURSIVE = _SetupRecursive()


def dir_matches_files_matcher_sdv__generic(setup: file_contents_utils.Setup[FilesMatcherModel],
                                           contents_matcher: GenericFilesMatcherSdv) -> GenericFileMatcherSdv:
    return file_contents_utils.sdv__generic(
        setup,
        contents_matcher,
    )
