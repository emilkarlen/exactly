import os
import sys

if len(sys.argv) == 2:
    file_to_process = None
    text_to_find = sys.argv[1]
elif len(sys.argv) == 3:
    file_to_process = sys.argv[1]
    text_to_find = sys.argv[2]
else:
    sys.stderr.write('Invalid usage.\nSyntax: [PATH] STRING' + os.linesep)
    sys.exit(1)


def filter_file(open_file):
    return [line
            for line in open_file.readlines()
            if text_to_find in line]


def process_stdin():
    for l in filter_file(sys.stdin):
        sys.stdout.write(l)


def process_file():
    with open(file_to_process) as f:
        result_lines = filter_file(f)

    with open(file_to_process, 'w') as f:
        f.writelines(result_lines)


if file_to_process is None:
    process_stdin()
else:
    process_file()
