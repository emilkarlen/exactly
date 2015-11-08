import pathlib

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant

DESCRIPTION = Description(
    'Makes a directory in the current directory',
    """
    Makes parent components, if needed.


    Does not fail if the given directory already exists.
    """,
    [InvokationVariant('DIRECTORY',
                       ''),
     ])


def make_dir_in_current_dir(directory_components: str) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    dir_path = pathlib.Path() / directory_components
    if dir_path.is_dir():
        return None
    try:
        dir_path.mkdir(parents=True)
    except FileExistsError:
        return 'Path exists, but is not a directory: {}'.format(dir_path)
    except NotADirectoryError:
        return 'Clash with existing file: {}'.format(dir_path)
    return None
