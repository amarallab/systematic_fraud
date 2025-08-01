import pandas as pd

from gustav import ncbi, utils


def gene_ensembl_2_gene_ncbi(df, taxon_ncbi, unambiguous=True):
    """
    Maps a dataframe, df, containing 'gene_ensembl' to 'gene_ncbi'.

    Input:
        df   dataframe, with 'gene_ensembl' as column or index
        taxon_ncbi  ncbi taxonomy ID (or 'all')
        unambiguous if TRUE will remove duplicated gene_ncbi and
                    duplicated gene_ensembl
    """

    gi = ncbi.gene_info(
        taxon_ncbi=taxon_ncbi, usecols=['gene_ncbi', 'dbxrefs'])

    helper = utils.stack_by_delimiter_in_column(
        gi, 'dbxrefs', '|')

    helper = helper[helper['dbxrefs'].str.startswith('Ensembl:')]
    helper['gene_ensembl'] = helper['dbxrefs'].copy().apply(
        lambda x: x[len('Ensembl:'):])
    ncbi2ensembl = helper[['gene_ncbi', 'gene_ensembl']].drop_duplicates()

    if unambiguous:
        c_ncbi = ncbi2ensembl['gene_ncbi'].value_counts()
        c_ensembl = ncbi2ensembl['gene_ensembl'].value_counts()

        ncbi2ensembl = ncbi2ensembl[
            ncbi2ensembl['gene_ncbi'].isin(c_ncbi[c_ncbi == 1].index) &
            ncbi2ensembl['gene_ensembl'].isin(c_ensembl[c_ensembl == 1].index)
            ]
    elif not unambiguous:
        pass
    else:
        raise AssertionError(
            'Input parameter unambiguous must either be True or False')

    in_column = 'gene_ensembl' in df.columns
    in_index = df.index.name == 'gene_ensembl'

    if not in_column and not in_index:
        raise AssertionError(
            'gene_ensembl neither defined as index or column')
    elif in_column and in_index:
        if not all(df.index == df['gene_ensembl']):
            raise AssertionError(
                'gene_ensembl defined in index and column but content differs')
    elif in_index:
        df = df.reset_index()

    df = pd.merge(ncbi2ensembl, df).drop('gene_ensembl', axis=1)

    if in_index:
        df = df.set_index('gene_ncbi')

    return df


def symbol_2_gene_ncbi(df, taxon_ncbi, unambiguous=True):
    """
    Maps a dataframe, df, containing 'symbol' to 'gene_ncbi'.

    Input:
        df   dataframe, with 'gene_ensembl' as column or index
        taxon_ncbi  ncbi taxonomy ID (or 'all')
        unambiguous if TRUE will remove duplicated gene_ncbi and
                    duplicated gene_ensembl
    """

    ncbi2symbol = ncbi.gene_info(
        taxon_ncbi=taxon_ncbi,
        usecols=['gene_ncbi', 'symbol_from_nomenclature_authority']
    ).rename(columns={'symbol_from_nomenclature_authority': 'symbol'})

    ncbi2symbol = ncbi2symbol[ncbi2symbol['symbol']
                              != '-'].copy().drop_duplicates()

    if unambiguous:
        c_ncbi = ncbi2symbol['gene_ncbi'].value_counts()
        c_symbol = ncbi2symbol['symbol'].value_counts()

        ncbi2symbol = ncbi2symbol[
            ncbi2symbol['gene_ncbi'].isin(c_ncbi[c_ncbi == 1].index) &
            ncbi2symbol['symbol'].isin(c_symbol[c_symbol == 1].index)
            ]
    elif not unambiguous:
        pass
    else:
        raise AssertionError(
            'Input parameter unambiguous must either be True or False')

    in_column = 'symbol' in df.columns
    in_index = df.index.name == 'symbol'

    if not in_column and not in_index:
        raise AssertionError(
            'symbol neither defined as index or column')
    elif in_column and in_index:
        if not all(df.index == df['symbol']):
            raise AssertionError(
                'symbol defined in index and column but content differs')
    elif in_index:
        df = df.reset_index()

    df = pd.merge(ncbi2symbol, df).drop('symbol', axis=1)

    if in_index:
        df = df.set_index('gene_ncbi')

    return df
