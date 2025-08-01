import pandas as pd


def stack_by_delimiter_in_column(df, column, delimiter):
    """
    Stacks dataframe according to delimiter in column

    Input:
        df          dataframe
        column      column with delimiter
        delimiter   delimiter (note: no regular expression)

    Output:
        stacked_df  stacked dataframe

    """

    index_name = df.index.name
    df.loc[:, column] = df.loc[:, column].astype(str)

    orig_index_name = df.index.name
    orig_column_order = df.columns

    df.index.name = 'original_index_used_before_splitting'
    df = df.reset_index()
    df.index.name = 'helper_index'

    f = (df[column].str.contains(
        delimiter, regex=False)) | (df[column].isnull())
    df_no_delimiter = df[~f]
    df_with_delimiter = df[f]

    ser_with_delimiter = df.loc[:, column]

    agg_values = []
    agg_indices = []

    for i, v in ser_with_delimiter.iteritems():
        vi = v.split(delimiter)
        indices = [i] * len(vi)

        agg_values.append(vi)
        agg_indices.append(indices)

    agg_values = flatten(agg_values)
    agg_indices = flatten(agg_indices)

    g = pd.DataFrame(
        data={'helper_index': agg_indices, column: agg_values})

    df_with_delimiter = pd.merge(
        df_with_delimiter.drop(column, 1).reset_index(),
        g)

    joined = pd.concat([
        df_no_delimiter.reset_index(),
        df_with_delimiter],
        sort=True
    )

    joined = joined.sort_values(
        ['original_index_used_before_splitting', column])
    joined = joined.drop('helper_index', 1)
    joined = joined.set_index('original_index_used_before_splitting')
    joined.index.name = orig_index_name
    joined = joined.loc[:, orig_column_order]
    joined.index.name = index_name

    return joined


def flatten(li):
    return [item for sublist in li for item in sublist]
