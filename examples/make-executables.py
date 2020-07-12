import itertools

from make import *

########################################
# Programs
########################################

DO_NOTHING = 'do-nothing'

HELLO_WORLD = 'hello-world'

HELLO_WORLD_WITHOUT_DASH = 'helloworld'

PRINT_NUMBER_OF_ARGUMENTS = 'print-number-of-arguments'

PRINT_NUMBER_OF_LINES_IN_FILE = 'print-number-of-lines-in-file'

PRINT_ONE_ARGUMENT_PER_LINE = 'print-one-argument-per-line'

CLASSIFY_FILES = 'classify-files-by-moving-to-appropriate-dir'

COPY_STDIN_TO_STDOUT = 'copy-stdin-to-stdout'

FILTER_LINES = 'filter-lines'

LIST_FILES_UNDER_CURRENT_DIRECTORY = 'list-files-under-current-directory'

REMOVE_ALL_FILES_IN_THE_CURRENT_DIRECTORY = 'remove-all-files-in-the-current-directory'

DO_SOMETHING_GOOD_WITH = 'do-something-good-with'

SYSTEM_UNDER_TEST = 'system-under-test'

MY_SETUP_HELPER_PROGRAM = 'my-setup-helper-program'

MY_ASSERT_HELPER_PROGRAM = 'my-assert-helper-program'

MY_STRING_TRANSFORMER_PROGRAM = 'my-string-transformer-program'

MY_HELPER_PROGRAM = 'my-helper-program'

MANIPULATE_DATABASE_CONTENTS = 'manipulate-database-contents'

PRINT_ENVIRONMENT_VARIABLES = 'print-environment-variables'

MY_CONTACTS_PROGRAM = 'my-contacts-program'

PROGRAM_THAT_WRITES_LOG_FILE = 'program-that-writes-log-file'

########################################
# Directories
########################################

intro_sub_dir = 'intro'
wiki_sub_dir = 'wiki'

wiki_hello_world_dir = Path(HELLO_WORLD)

src_base_dir = Path('executables-src')
first_step_dir = Path('first-step')
sandbox_dir = Path('sandbox-directories')
symbols_dir = Path('symbols')
home_dir = Path('home-directories')
cleanup_dir = Path('cleanup')
dir_contents_dir = Path('dir-contents')
external_programs_dir = Path('external-programs')
setup_dir = Path('setup')
file_transformations_dir = Path('file-transformations')
suites_dir = Path('suites')

readme_examples_root_dir = 'readme-file-examples'

readme_contacts_dir = Path('contacts')
readme_classify_dir = Path('classify')
readme_sandbox_dir = Path('sandbox')


########################################
# Directories setup
########################################

def st(target_base: Path, file_name: str) -> SourceAndTarget:
    return SourceAndTarget(src_base_dir / file_name,
                           target_base / file_name)


def sts(target_base: Path, file_names: List[str]) -> List[SourceAndTarget]:
    return [st(target_base, file_name) for file_name in file_names]


def do_nothing(target_file: Path) -> SourceAndTarget:
    return SourceAndTarget(src_base_dir / DO_NOTHING,
                           target_file)


def do_nothing_list(target_base: Path, target_file_names: List[str]) -> List[SourceAndTarget]:
    return [do_nothing(target_base / file_name) for file_name in target_file_names]


README_FILES = itertools.chain.from_iterable([
    sts(readme_contacts_dir,
        [MY_CONTACTS_PROGRAM,
         ]),
    sts(readme_classify_dir,
        [CLASSIFY_FILES,
         ]),
    sts(readme_sandbox_dir,
        [HELLO_WORLD,
         ]),
    sts(Path('bin'),
        [FILTER_LINES,
         ]),
    do_nothing_list(
        Path('external-programs'),
        [MY_ASSERT_HELPER_PROGRAM,
         MY_SETUP_HELPER_PROGRAM,
         MY_STRING_TRANSFORMER_PROGRAM,
         SYSTEM_UNDER_TEST,
         ]),
    sts(Path('transform'),
        [PROGRAM_THAT_WRITES_LOG_FILE]
        ),
    sts(Path('git-hook'),
        ['prepare-commit-msg']
        ),
])

BUILTIN_HELP_FILES = [
    st(Path('.'), HELLO_WORLD_WITHOUT_DASH),
]

INTRO_FILES = itertools.chain.from_iterable(
    [
        sts(first_step_dir,
            [HELLO_WORLD,
             FILTER_LINES,
             ]),

        sts(sandbox_dir,
            [HELLO_WORLD,
             CLASSIFY_FILES,
             REMOVE_ALL_FILES_IN_THE_CURRENT_DIRECTORY,
             ]),

        sts(symbols_dir / 'bin',
            [PRINT_NUMBER_OF_ARGUMENTS,
             PRINT_ONE_ARGUMENT_PER_LINE,
             CLASSIFY_FILES,
             PRINT_NUMBER_OF_LINES_IN_FILE,
             FILTER_LINES,
             ]),

        sts(file_transformations_dir / 'bin',
            [PRINT_ONE_ARGUMENT_PER_LINE,
             ]),

        do_nothing_list(cleanup_dir,
                        [MANIPULATE_DATABASE_CONTENTS,
                         MY_HELPER_PROGRAM,
                         ]),

        do_nothing_list(external_programs_dir,
                        [MY_ASSERT_HELPER_PROGRAM,
                         MY_SETUP_HELPER_PROGRAM,
                         SYSTEM_UNDER_TEST,
                         ]),

        do_nothing_list(home_dir / 'bin',
                        [DO_SOMETHING_GOOD_WITH,
                         ]),

        sts(setup_dir,
            [COPY_STDIN_TO_STDOUT,
             REMOVE_ALL_FILES_IN_THE_CURRENT_DIRECTORY,
             PRINT_ENVIRONMENT_VARIABLES,
             LIST_FILES_UNDER_CURRENT_DIRECTORY,
             ]),
    ])

WIKI_FILES = itertools.chain.from_iterable(
    [
        sts(wiki_hello_world_dir,
            [HELLO_WORLD,
             ]),

    ])

REAL_WORLD_FILES = itertools.chain.from_iterable(
    [
        sts(Path('git-hook'),
            ['prepare-commit-msg']
            ),
    ])

SUB_DIR_CONFIGS = [
    (intro_sub_dir, INTRO_FILES),
    (readme_examples_root_dir, README_FILES),
    ('builtin-help', BUILTIN_HELP_FILES),
    (wiki_sub_dir, WIKI_FILES),
    ('real-world', REAL_WORLD_FILES),
]

if __name__ == '__main__':
    main(SUB_DIR_CONFIGS)
