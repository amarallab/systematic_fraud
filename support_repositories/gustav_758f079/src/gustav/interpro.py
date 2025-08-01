import pandas as pd

from gustav import inout


def interpro(dataset):
    """
    Interpro

    dataset: 'vip_taxa'
    """

    data_version = inout.get_data_version('interpro')

    p = inout.get_input_path(
        'ebi/interpro/{}/interpro_id_2_name.parquet'.format(
            data_version)
    )
    df_names = pd.read_parquet(p)

    if dataset == 'vip_taxa':

        p = inout.get_input_path(
            'ebi/interpro/{}/gene2domain_vip_taxa.parquet'.format(
                data_version)
        )
        df = pd.read_parquet(p)

    else:
        raise AssertionError('selected dataset not supported')

    df = pd.merge(df, df_names)

    return df
