import os

import pandas as pd

from preparator import inout, utils
from preparator import served


def gene_to_drug():
    """
    Maps individual genes to drugs via the
    gene symbol.
    """

    data_version = inout.get_data_version('drugbank')

    p_drugbank = inout.get_input_path(
        'manual/drugbank/{}'.format(data_version))

    def read_targets(target_type):

        subs = [
            'approved',
            'biotech',
            'experimental',
            'illicit',
            'investigational',
            'nutraceutical',
            'small_molecule',
            'withdrawn'
        ]

        agg = []
        for sub in subs:

            p = os.path.join(
                p_drugbank,
                'drugbank_{}_target_polypeptide_ids.csv'.format(sub),
                '{}.csv'.format(target_type))

            d = pd.read_csv(p)
            d.loc[:, 'status'] = sub
            agg.append(d)

        df = pd.concat(agg)
        df = utils.lower_captions_and_replace_spaces(df)

        df = utils.stack_by_delimiter_in_column(
            df,
            'drug_ids', ';')

        return df

    organisms = {
        9606: 'Humans'
    }

    for target_type in ['pharmacologically_active']:
        all_targets = read_targets(target_type)

        for taxon, species in organisms.items():
            df = all_targets[all_targets['species'] == species].copy()

            df = df[['gene_name', 'drug_ids', 'status']].rename(
                columns={
                    'drug_ids': 'drugbank_id',
                    'gene_name': 'symbol_ncbi'
                }
            ).drop_duplicates()

            gi = served.ncbi_gene_info(
                ['taxon_ncbi', 'symbol_ncbi', 'gene_ncbi']
            )

            gi = gi[gi['taxon_ncbi'] == taxon]

            # merge by gene symbol. note that drugbank has some with unofficial
            # symbols -> decided against heuristics since
            # records possibly not trustfull
            df = pd.merge(
                gi[['symbol_ncbi', 'gene_ncbi']],
                df,
                how='inner'
            ).drop(columns=['symbol_ncbi']).drop_duplicates()

            df = df.sort_values(
                ['status', 'gene_ncbi'])

            p = 'drugbank/{}/gene_to_drug_{}_{}.parquet'.format(
                data_version, int(taxon), target_type)
            inout.export_plain_table(df, p)

    return


def drug_to_name():
    """
    Get drug names
    """

    data_version = inout.get_data_version('drugbank')

    p_drugbank = inout.get_input_path(
        'manual/drugbank/{}'.format(data_version))
    p = os.path.join(
        p_drugbank, 'drugbank vocabulary.csv')

    df = pd.read_csv(p)
    df = utils.lower_captions_and_replace_spaces(df)

    p = 'drugbank/{}/drug_to_name.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

