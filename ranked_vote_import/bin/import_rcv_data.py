import argparse
from ranked_vote_import import FORMATS
from ranked_vote.format import write_ballots_fh
from sys import stdout, stderr

TERMINAL_RESET = '\033[0m'
TERMINAL_BOLD = '\033[1m'
TERMIANL_GREEN = '\033[92m'

FORMAT_METADATA = TERMINAL_BOLD+TERMIANL_GREEN+'    {}: '+TERMINAL_RESET+'{}'


def import_rcv_data(input_format, files):
    if input_format not in FORMATS:
        raise ValueError('Format {} not understood.'.format(input_format))

    reader = FORMATS[input_format](files)

    fh = stdout

    write_ballots_fh(fh, reader)

    metadata = reader.get_metadata()

    for mk, mv in metadata.items():
        print(FORMAT_METADATA.format(mk, mv), file=stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_format')
    parser.add_argument('files', nargs='+')

    import_rcv_data(**vars(parser.parse_args()))


if __name__ == '__main__':
    main()
