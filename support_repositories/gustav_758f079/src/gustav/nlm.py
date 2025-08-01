import pandas as pd

from gustav import inout


def mesh(dataset, columns=None):
    """
    dataset: 'ui2mn' or for full tables:
             'descriptor', 'supplement',
             'qualifier'

    columns: columns to load
    """

    data_version = inout.get_data_version('mesh')

    p = inout.get_input_path(
        'nlm/mesh/{}/{}.parquet'.format(
            data_version, dataset)
    )
    df = pd.read_parquet(p, columns=columns)

    return df
