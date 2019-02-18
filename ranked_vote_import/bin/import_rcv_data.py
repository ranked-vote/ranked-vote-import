import argparse
import json
import re
from sys import stdout, stderr
from typing import Dict

from ranked_vote.format import write_ballots, write_ballots_fh
from ranked_vote_import import FORMATS, NORMALIZERS

TERMINAL_RESET = '\033[0m'
TERMINAL_BOLD = '\033[1m'
TERMINAL_GREEN = '\033[92m'

FORMAT_METADATA = TERMINAL_BOLD + TERMINAL_GREEN + '  {}: ' + TERMINAL_RESET + '{}'


def import_rcv_data(input_format, files, output, normalize=False, params: Dict = None):
    if input_format not in FORMATS:
        raise ValueError('Format {} not understood.'.format(input_format))

    ballots = reader = FORMATS[input_format](files, params)
    if normalize:
        normalizer = NORMALIZERS[input_format]()
        ballots = (normalizer.normalize(ballot) for ballot in reader)

    if output is None:
        print('Writing data to stdout and not writing metadata.', file=stderr)
        write_ballots_fh(stdout, ballots)
        meta_file = None
    else:
        write_ballots(output, ballots)
        meta_file = re.sub(r'\.csv(\.gz)?$', '', output) + '.json'

    metadata = reader.get_metadata()
    metadata['normalized'] = normalize

    if meta_file is not None:
        with open(meta_file, 'w') as meta_fh:
            json.dump(metadata, meta_fh, sort_keys=True, indent=2)

    print(TERMINAL_BOLD + TERMINAL_GREEN + 'Done Converting.' + TERMINAL_RESET, file=stderr)
    for mk, mv in metadata.items():
        if isinstance(mv, list):
            print(FORMAT_METADATA.format(mk, ''), file=stderr)
            for item in mv:
                print('    ' + str(item), file=stderr)
        else:
            print(FORMAT_METADATA.format(mk, mv), file=stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_format')
    parser.add_argument('files', nargs='+')
    parser.add_argument('--normalize', action='store_true')
    parser.add_argument('--params', type=json.loads, default=dict())
    parser.add_argument('-o', '--output')

    import_rcv_data(**vars(parser.parse_args()))


if __name__ == '__main__':
    main()
