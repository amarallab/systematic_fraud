import pandas as pd

from gustav import inout


def hagr(dataset):
    """
    Human Ageing Genomic Resources (HAGR)
    https://www.genomics.senescence.info/index.php

    dataset: 'genage_human', 'genage_model_organisms',
                'longevitymap'
    """

    data_version = inout.get_data_version('hagr')

    p = inout.get_input_path(
        'hagr/{}/{}.parquet'.format(
            data_version, dataset)
    )
    df = pd.read_parquet(p)

    return df
