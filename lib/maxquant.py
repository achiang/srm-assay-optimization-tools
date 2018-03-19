import re
import pandas as pd
from contextlib import suppress
from os import path


def _clean_acetylation(x):
    """Replace a sequence like: (ac)SGGA with S[+42]GGA

    The (ac) should be replaced completely, and a [+42] should be inserted
    after the first character, after the (ac).
    """
    def twiddle(match):
        return match['char_after'] + '[+42]'

    # Create two capture groups, one named 'ac', second named 'char_after'
    needle = re.compile('(?P<ac>\(ac\))(?P<char_after>\w{1})')
    return needle.sub(twiddle, x)


def _clean(x):
    x = (
        x
        .replace('_', '')
        .replace('(ox)', '[+16]')
        .replace('C', 'C[+57]'))
    x = _clean_acetylation(x)
    return x


def _copy_and_insert_column_after(df, source, target):
    df.insert(
        df.columns.get_loc(source) + 1,
        target,
        df[source])


def _clean_target_column(df, column_name):
    df[column_name] = df[column_name].apply(_clean)


def to_skyline(input_, out=None):
    with out or suppress():
        print('Converting {}'.format(input_))

    source_column_name = 'Modified_sequence'
    target_column_name = source_column_name + '_Skyline'

    df = pd.read_csv(input_, delimiter='\t')

    _copy_and_insert_column_after(df, source_column_name, target_column_name)
    _clean_target_column(df, target_column_name)

    out_name = path.splitext(input_)[0] + '_to_skyline.csv'

    df.to_csv(out_name)
