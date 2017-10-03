import os
import sys

GET_EMAIL_COMMAND = 'get-email-of'
NAME_OPTION = '--name'


def exit_error(msg: str):
    sys.stderr.write(msg + os.linesep)
    sys.exit(1)


def parse_line(line: str):
    parts = line.split(':')
    if len(parts) != 2:
        exit_error('Invalid address book entry: ' + line)
    return parts[0].strip(), parts[1].strip()


if len(sys.argv) <= 1:
    exit_error('Missing command')

if sys.argv[1] != GET_EMAIL_COMMAND:
    exit_error('Invalid command: ' + sys.argv[1])

if len(sys.argv) != 4:
    exit_error('Invalid arguments')

if sys.argv[2] != NAME_OPTION:
    exit_error('Missing name option: ' + NAME_OPTION)

name_to_lookup = sys.argv[3]

for entry_line in sys.stdin:
    name, email = parse_line(entry_line)
    if name == name_to_lookup:
        print(email)
        sys.exit()

sys.stderr('Name not in address book: ' + name_to_lookup)
