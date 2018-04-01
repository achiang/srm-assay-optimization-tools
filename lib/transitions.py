"""
Convert an input file of SRM assay transitions into a user-specified number
of output files, with a uniform distribution of retention times, suitable
for consumption by a TSQ Quantiva.
"""

import pandas as pd
import sys
from contextlib import suppress
from os import path


RT_MIN = 'Retention Time (min)'


def _dedupe_compounds_by_rt(df):
    # returns a new DataFrame
    return (
        df
        .drop_duplicates(subset=['Compound_by_RT'])
        .sort_values(by=[RT_MIN])
        .reset_index())


def _distribute_across_methods(df, num_methods):
    df['Method'] = (df.index.astype(int) % int(num_methods)) + 1


def _backfill_compounds_by_rt_with_methods(df_orig, df_methods):
    # Step 1: left join the original DataFrame with the new DataFrame which
    # has uniformly distributed each unique compound/retention time combo
    # across the user-specified number of methods.
    #
    # Since the original DataFrame is larger than the distributed one, the
    # new DataFrame will have holes in the 'Method' column
    merged = df_orig.merge(df_methods, how='left')[[
        'Method',
        'Compound',
        'Retention Time (min)',
        'Precursor (m/z)',
        'Product (m/z)',
        'Collision Energy (V)',
        'RF Lens (V)']]

    # Step 2: fill in the holes. Works because df_methods was sorted by RT_MIN
    merged.fillna(method='ffill', inplace=True)
    return merged


def _insert_constants(df, rt_window_value):
    RT_WINDOW_MIN = 'RT Window (min)'
    df.insert(
        df.columns.get_loc(RT_MIN) + 1,
        RT_WINDOW_MIN,
        rt_window_value)
    df.insert(
        df.columns.get_loc(RT_WINDOW_MIN) + 1,
        'Polarity',
        'Positive')


def _write_csv_per_method(input_, df, out=None):
    groups = df.groupby(df['Method'])
    for (frameno, frame) in groups:
        # Don't need/want to output our calculated method number, as it's a
        # concept that only makes sense to the user
        del frame['Method']
        output = path.splitext(input_)[0] + '_m{:02d}.csv'.format(int(frameno))
        (frame
            .sort_values(by=RT_MIN)
            .to_csv(output, index=False))

        with out or suppress():
            print('Created', output)


def split_to_quantiva(input_, num_methods, rt_window_value, out=None):
    df = pd.read_csv(input_)

    # Compound_by_RT is the unique value, which we wish to uniformly distribute
    # across the desired number of methods. Add it to the original DataFrame
    # first, so that we can use it as a join condition later on, after
    # evenly distributing the transitions.
    df['Compound_by_RT'] = list(zip(df['Compound'], df[RT_MIN]))

    deduped = _dedupe_compounds_by_rt(df)
    _distribute_across_methods(deduped, num_methods)

    filled = _backfill_compounds_by_rt_with_methods(df, deduped)
    _insert_constants(filled, rt_window_value)

    _write_csv_per_method(input_, filled, out=out)


if __name__ == "__main__":
    split_to_quantiva(*sys.argv[1:])
