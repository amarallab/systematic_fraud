import pandas as pd

from gustav import inout


def gene_to_drug(taxon, target_type):
    """
    taxon:   ncbi taxonomy ID, e.g.: 9606
    target_type:  e.g.: 'pharmacologically_active'
    """

    data_version = inout.get_data_version('drugbank')

    p = inout.get_input_path(
        'drugbank/{}/gene_to_drug_{}_{}.parquet'.format(
            data_version, int(taxon), target_type))

    df = pd.read_parquet(p)

    return df


def drug_to_name():
    """
    Loads names of drugbank_ids
    """

    data_version = inout.get_data_version('drugbank')

    p = inout.get_input_path(
        'drugbank/{}/drug_to_name.parquet'.format(
            data_version))

    df = pd.read_parquet(p)

    return df
