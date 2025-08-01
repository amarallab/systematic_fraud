import pandas as pd

from preparator import inout, served


def depmap_essentials():
    """
    Get common essentials from depmap, consisting of
    a) curation by depmap; b) those found by them
    in Achilles project

    """

    data_version = inout.get_data_version('depmap')

    p = inout.get_input_path(
        'manual/figshare/depmap_20q2_public/version_4/common_essentials.csv'
    )
    df_curated = pd.read_csv(p)

    p = inout.get_input_path(
        'manual/figshare/depmap_20q2_public/version_4/Achilles_common_essentials.csv'
    )
    df_achilles = pd.read_csv(p)

    df = pd.concat(
        [df_curated, df_achilles]
    )

    df = pd.Series(
        df['gene'].str.extract('(.*) ', expand=False).str.strip(
        ).unique()).to_frame('symbol_ncbi')

    gi = served.ncbi_gene_info(['gene_ncbi', 'symbol_ncbi', 'taxon_ncbi'])
    gi = gi[gi['taxon_ncbi'] == 9606][['gene_ncbi', 'symbol_ncbi']]
    gi['essential'] = gi['symbol_ncbi'].isin(df['symbol_ncbi'])
    hitters = gi[['gene_ncbi', 'essential']].reset_index(drop=True)

    p_out = 'figshare/depmap/{}/combined_essentials.parquet'.format(
        data_version)
    inout.export_plain_table(hitters, p_out)

    return
