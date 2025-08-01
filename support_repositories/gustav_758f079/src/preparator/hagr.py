import os

import pandas as pd

from preparator import inout
from preparator import served


def hagr():

    # general settings
    gi = served.ncbi_gene_info(['gene_ncbi', 'taxon_ncbi'])
    data_version = inout.get_data_version('hagr')

    # GenAge Human

    p = inout.get_input_path(
        'manual/hagr/{}/genage_human/genage_human.csv'.format(data_version)
    )
    df = pd.read_csv(p).rename(columns={'entrez gene id': 'gene_ncbi'})

    df = df[['gene_ncbi', 'why']].drop_duplicates()

    df = pd.merge(df, gi, how='left')
    if any(df['taxon_ncbi'] != 9606):
        raise AssertionError('at least one gene is not human')
    else:
        df = df.loc[:, ['gene_ncbi', 'why']]

    if df['gene_ncbi'].value_counts().max() > 1:
        raise AssertionError('at least one gene is repeated')

    p = 'hagr/{}/genage_human.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

    # GenAge Model Organisms

    p = inout.get_input_path(
        'manual/hagr/{}/genage_model_organisms/genage_models.csv'.format(
            data_version)
    )

    df = pd.read_csv(p).rename(columns={'entrez gene id': 'gene_ncbi'})

    df = pd.merge(df, gi)
    # some provided genes are human not model organism (6 records on 2020-12-21)
    df = df[df['taxon_ncbi'] != 9606]

    df = df[[
        'taxon_ncbi', 'gene_ncbi',
        'lifespan effect', 'longevity influence',
        'avg lifespan change (max obsv)'
    ]]

    df.columns = [
        x.replace('(', '').replace(')', '').replace(' ', '_') for x in df.columns
    ]
    p = 'hagr/{}/genage_model_organisms.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

    # Longevity Map

    p = inout.get_input_path(
        'manual/hagr/{}/longevitymap/longevity.csv'.format(data_version)
    )
    df = pd.read_csv(p).rename(
        columns={
            'entrez gene id': 'gene_ncbi',
            'PubMed': 'pubmed_id'
        })
    df.columns = [
        x.replace('(s)', 's').lower() for x in df.columns
    ]
    df = df.reindex(columns=['pubmed_id', 'genes',
                             'variants', 'association', 'population'])
    df['association'] = df['association'].str.lower()
    p = 'hagr/{}/longevitymap.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)
