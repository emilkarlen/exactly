import os
import pathlib
import sys


def is_good_file(a_file: pathlib.Path):
    contents = a_file.read_text()
    return good_token in contents


def check_dir(input_dir: pathlib.Path,
              output_good: pathlib.Path,
              output_bad: pathlib.Path,
              ):
    for input_path in input_dir.iterdir():
        if input_path.is_dir():
            check_dir(input_path,
                      output_good / input_path.name,
                      output_bad / input_path.name)
            input_path.rmdir()

        elif input_path.is_file():
            if is_good_file(input_path):
                target_dir = output_good
            else:
                target_dir = output_bad
            target_dir.mkdir(exist_ok=True, parents=True)
            input_path.rename(target_dir / input_path.name)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.stderr.write('Invalid usage.\nSyntax: GOOD-TOKEN INPUT-DIR OUTPUT-DIR' + os.linesep)
        sys.exit(1)

    good_token = sys.argv[1]

    root_input_dir = pathlib.Path(sys.argv[2])
    root_output_dir = pathlib.Path(sys.argv[3])

    check_dir(root_input_dir,
              root_output_dir / 'good',
              root_output_dir / 'bad')
