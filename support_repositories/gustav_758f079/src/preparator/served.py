import pandas as pd

from preparator import inout


def ncbi_gene_info(usecols=None):
    """
    Loads entire ncbi gene_info table, as previously
    processed by gustav

    Input:
    usecols         columns to load
    """

    print('Called served.ncbi_gene_info. Ensure that updated.')

    data_version = inout.get_data_version('gene_info')

    p = inout.get_output_path(
        'ncbi/data/{}/gene_info.parquet'.format(
            data_version))
    df = pd.read_parquet(p, columns=usecols)

    return df


def ncbi_gene2pubmed():
    """
    Loads gene2pubmed
    """

    print('Called served.gene2pubmed. Ensure that updated.')

    data_version = inout.get_data_version('gene2pubmed')

    p = inout.get_output_path(
        'ncbi/data/{}/gene2pubmed.parquet'.format(
            data_version))
    df = pd.read_parquet(p)

    return df


def uniprot_to_gene_ncbi(dataset):
    """
    Loads uniprot to gene_ncbi mapper
    """

    print('Called served.uniprot_to_gene_ncbi. Ensure that updated.')

    data_version = inout.get_data_version('uniprot')

    if dataset == 'vip':

        p = inout.get_output_path(
            'ebi/uniprot/{}/protein_uniprot_to_gene_ncbi_{}_taxa.parquet'.format(
                data_version, dataset))
        df = pd.read_parquet(p)

    else:
        raise AssertionError(
            'Dataset not implemented yet.')

    return df
