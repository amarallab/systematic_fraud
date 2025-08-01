import pandas as pd

from gustav import inout


def targetscan(dataset):
    """
    Targetscan

    dataset: 'predicted_targets', 'predicted_targets_context_scores',
                'gene_info'
    """

    data_version = inout.get_data_version('targetscan')

    p = inout.get_input_path(
        'targetsan/data/{}/{}.parquet'.format(
            data_version, dataset)
    )
    df = pd.read_parquet(p)

    return df
