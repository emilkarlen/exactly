import sys

import re
import subprocess

issue_pattern = re.compile('([A-Z]{2,3}-[0-9]{1,5})', re.I)
merge_pattern = re.compile('^.*(merge)+.*$', re.I)


def is_merge(commit_message):
    for line in commit_message.splitlines():
        m = re.search(merge_pattern, line)
        if m:
            return True
    return False


def has_issue_issue(file_name):
    return any_line_contains_pattern(file_name, issue_pattern)


def any_line_contains_pattern(file_name, reg_exp_pattern):
    with open(file_name, 'r') as message_file:
        lines = message_file.readlines()
        for line in lines:
            m = re.search(reg_exp_pattern, line)
            if m:
                return True
        return False


def get_issue_from_branch_name():
    current_branch = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD'],
                                             universal_newlines=True)
    current_branch = current_branch.strip()
    m = re.match(issue_pattern, current_branch)
    if m:
        return m.group(0)
    else:
        print('Current branch name does not include an issue number in its name : %s' % current_branch)


def get_issue_from_commit_message(message):
    m = re.match(issue_pattern, message)
    if m:
        return m.group(0)
    else:
        return None


def add_issue_number_to_commit(file_name, issue):
    with open(file_name, 'r') as message_file:
        lines = message_file.readlines()
        lines[0] = issue + ' : ' + lines[0]
    with open(file_name, 'w') as message_file:
        message_file.write(''.join(lines))


commit_message_file = sys.argv[1]

try:
    with open(commit_message_file) as message_file:
        commit_message = message_file.read()
except IOError:
    print('Unable to read commit message file ' + commit_message_file)
    sys.exit(1)

if is_merge(commit_message):
    sys.exit(0)

issue_of_commit_message = get_issue_from_commit_message(commit_message)

if issue_of_commit_message is None:
    issue_number = get_issue_from_branch_name()
    if issue_number:
        add_issue_number_to_commit(commit_message_file, issue_number)
    else:
        print('Commit does not contain issue number.')
        sys.exit(1)
else:
    issue_of_branch_name = get_issue_from_branch_name()
    if issue_of_branch_name is not None:
        if issue_of_branch_name != issue_of_commit_message:
            print('Mismatch of issue of branch and commit message: %s != %s' % (issue_of_branch_name,
                                                                                issue_of_commit_message))
            sys.exit(1)

sys.exit(0)
