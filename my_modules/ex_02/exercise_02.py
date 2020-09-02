import argparse


def print_file_content(file):
    with open(file) as file_object:
        contents = file_object.read()
    print(contents)


def write_list_to_file(output_file, lst):
    tuplelst = tuple(lst)
    write_to_file(output_file, tuplelst)


def write_to_file(output_file, tuplelst):
    with open(output_file, 'w') as file_object:
        for n in tuplelst:
            file_object.write(n + '\n')


def read_file(input_file):
    with open(input_file) as file_object:
        content = file_object.readlines()

        for line in content:
            print(line.strip().split(', '))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='A program that writes to a file')
    parser.add_argument('path', help='Path to input file')
    parser.add_argument('-o', '--output_name',
                        help='The output file to write to')
    parser.add_argument(
        '-e', '--extra', help='Extra words to be written to the file')
    args = parser.parse_args()

    if not args.output_name:
        read_file(args.path)
    elif args.output_name and args.extra:
        write_list_to_file(args.output_file, args.extra)
