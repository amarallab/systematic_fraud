import os

import pandas as pd
from preparator import inout, mapper


def _lower_captions(df):
    df.columns = [x.lower() for x in df.columns]
    return df


def human_protein_atlas():
    """
    Processes HPA, the Human Protein Atlas
    """

    data_version = inout.get_data_version('human_protein_atlas')

    p_base = inout.get_input_path('manual/hpa/{}'.format(data_version))

    df = pd.read_csv(
        os.path.join(p_base, 'subcellular_location.tsv'),
        sep='\t'
    )

    df = df.drop('Gene name', axis=1)
    df = df.rename(columns={'Gene': 'gene_ensembl'})

    df = _lower_captions(df)
    df.columns = [x.replace(' ', '_') for x in df.columns]

    df = mapper.gene_ensembl_2_gene_ncbi(df, taxon_ncbi=9606, unambiguous=True)

    p = 'human_protein_atlas/{}/subcellular_location.parquet'.format(
        data_version, )
    inout.export_plain_table(df, p)

    return
