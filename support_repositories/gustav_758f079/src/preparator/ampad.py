import pandas as pd

from preparator import inout, served


def _lower_captions(df):
    df.columns = [x.lower() for x in df.columns]
    return df


def agora():
    """
    Target genes nominated by agora
    """

    data_version = inout.get_data_version('ampad/agora')

    p = inout.get_input_path(
        f'manual/ampad/agora/{data_version}/gene-list.csv')

    data_version = inout.get_data_version('ampad/agora')

    p = inout.get_input_path(
        f'manual/ampad/agora/{data_version}/genes-list.csv')
    df = pd.read_csv(p)

    gi = served.ncbi_gene_info(['gene_ncbi', 'taxon_ncbi', 'symbol_from_nomenclature_authority']).rename(
        columns={
            'symbol_from_nomenclature_authority': 'hgnc_symbol'
        }
    )
    df = pd.merge(gi[gi['taxon_ncbi'] == 9606][['gene_ncbi', 'hgnc_symbol']], df).drop(
        'hgnc_symbol', axis='columns').set_index('gene_ncbi', verify_integrity=True).reset_index()

    p = 'ampad/agora/{}/genes-list.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

    return
