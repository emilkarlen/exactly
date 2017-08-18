import os
import pathlib
import sys

if len(sys.argv) != 2:
    sys.stderr.write('Invalid usage.\nSyntax: ROOT-DIR' + os.linesep)
    sys.exit(1)

root_dir = pathlib.Path(sys.argv[1])

good_token = 'GOOD'

input_dir = root_dir / 'input-files'
output_dir = root_dir / 'output-files'

output_good_dir = output_dir / 'good'
output_bad_dir = output_dir / 'bad'


def is_good_file(a_file):
    contents = a_file.read_text()
    return good_token in contents


for input_file in input_dir.iterdir():
    if is_good_file(input_file):
        target_dir = output_good_dir
    else:
        target_dir = output_bad_dir
    input_file.rename(target_dir / input_file.name)
