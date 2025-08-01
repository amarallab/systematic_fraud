import pandas as pd

from gustav import inout


def depmap_essentials():
    """
    Get common essentials from depmap, consisting of
    a) curation by depmap; b) those found by them
    in Achilles project

    """

    data_version = inout.get_data_version('depmap')

    p = inout.get_input_path(
        'figshare/depmap/{}/combined_essentials.parquet'.format(
            data_version)
    )

    df = pd.read_parquet(p)

    return df
