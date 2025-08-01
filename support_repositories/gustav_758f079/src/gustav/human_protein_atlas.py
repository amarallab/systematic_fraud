import pandas as pd

from gustav import inout


def human_protein_atlas(dataset):
    """
    Interpro

    dataset: 'subcellular_location'
    """

    data_version = inout.get_data_version('human_protein_atlas')

    p = inout.get_input_path(
        'human_protein_atlas/{}/{}.parquet'.format(
            data_version, dataset)
    )
    df = pd.read_parquet(p)

    return df
