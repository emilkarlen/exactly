import re
import subprocess
import sys
from typing import Optional

ISSUE_PATTERN = re.compile('([A-Z]{2,3}-[0-9]{1,5})', re.I)
MERGE_PATTERN = re.compile('^.*(merge)+.*$', re.I)


def exit_error(error_message: str):
    print(error_message)
    sys.exit(1)


def is_merge(commit_message: str):
    return any((
        bool(re.search(MERGE_PATTERN, line))
        for line in commit_message.splitlines()
    ))


def get_issue_id_from_branch_name() -> str:
    current_branch = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD'],
                                             universal_newlines=True)
    current_branch = current_branch.strip()
    m = re.match(ISSUE_PATTERN, current_branch)
    if m:
        return m.group(0)
    else:
        exit_error('Current branch name does not include an issue ID : {}'.format(current_branch))


def get_issue_from_commit_message(message: str) -> Optional[str]:
    m = re.match(ISSUE_PATTERN, message)
    if m:
        return m.group(0)
    else:
        return None


def add_issue_id_to_commit(message_file_name: str, issue_id: str):
    with open(message_file_name, 'r') as message_file:
        lines = message_file.readlines()
        lines[0] = issue_id + ' : ' + lines[0]
    with open(message_file_name, 'w') as message_file:
        message_file.write(''.join(lines))


def get_commit_message(commit_message_file: str) -> str:
    try:
        with open(commit_message_file) as message_file:
            return message_file.read()
    except IOError:
        exit_error('Unable to read commit message file ' + commit_message_file)


def main():
    commit_message_file = sys.argv[1]

    commit_message = get_commit_message(commit_message_file)

    if is_merge(commit_message):
        sys.exit(0)

    issue_id_of_branch_name = get_issue_id_from_branch_name()
    mb_issue_id_of_commit_message = get_issue_from_commit_message(commit_message)

    if mb_issue_id_of_commit_message is None:
        add_issue_id_to_commit(commit_message_file, issue_id_of_branch_name)
    else:
        if issue_id_of_branch_name != mb_issue_id_of_commit_message:
            exit_error('Mismatch of issue ID of branch name and commit message:\n{} != {}'.format(
                issue_id_of_branch_name,
                mb_issue_id_of_commit_message))


if __name__ == '__main__':
    main()
    sys.exit(0)
