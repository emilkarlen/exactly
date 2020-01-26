from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher import file_or_dir_contents_doc
from exactly_lib.test_case_utils.file_matcher.impl import file_contents_utils
from exactly_lib.test_case_utils.file_matcher.impl.file_contents_utils import ModelConstructor
from exactly_lib.test_case_utils.files_matcher import models
from exactly_lib.test_case_utils.generic_dependent_value import Sdv, sdv_of_constant_primitive
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, GenericFileMatcherSdv
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, GenericFilesMatcherSdv

NAMES = file_contents_utils.NamesSetup(
    file_check_properties.DIR_CONTENTS,
    file_properties.FileType.DIRECTORY,
    syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT,
)


class _NonRecursiveModelConstructor(file_contents_utils.ModelConstructor[FilesMatcherModel]):

    def make_model(self, model: FileMatcherModel) -> FilesMatcherModel:
        return models.non_recursive(model.path)


class _RecursiveModelConstructor(file_contents_utils.ModelConstructor[FilesMatcherModel]):

    def make_model(self, model: FileMatcherModel) -> FilesMatcherModel:
        return models.recursive(model.path)


DOCUMENTATION_SETUP = file_contents_utils.DocumentationSetup(
    NAMES,
    file_or_dir_contents_doc.RECURSION_OPTIONS,
    file_or_dir_contents_doc.get_recursion_option_description,
)

MODEL_CONSTRUCTOR__NON_RECURSIVE = sdv_of_constant_primitive(_NonRecursiveModelConstructor())
MODEL_CONSTRUCTOR__RECURSIVE = _RecursiveModelConstructor()


def dir_matches_files_matcher_sdv__generic(
        model_constructor: Sdv[ModelConstructor[FilesMatcherModel]],
        contents_matcher: GenericFilesMatcherSdv,
) -> GenericFileMatcherSdv:
    return file_contents_utils.sdv__generic(
        NAMES,
        model_constructor,
        contents_matcher,
    )
