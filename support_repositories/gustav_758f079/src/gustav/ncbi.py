import os

import pandas as pd
from gustav import inout, utils


def biosystems(taxon_ncbi):
    """
    NCBI Biosystems

    Input:
    taxon_ncbi      int corresponding to ncbi_taxonomy identifier
    """

    data_version = inout.get_data_version('biosystems')

    p = 'ncbi/biosystems/{}/biosystems_{}.parquet'.format(data_version, int(taxon_ncbi))
    df = pd.read_parquet(inout.get_input_path(p))

    return df


def bioprojects(pubs=False, authors=False):
    # later, implement publication searching from the json file

    data_version = inout.get_data_version('bioprojects')

    p = 'ncbi/bioprojects/{}/bioprojects.parquet'.format(data_version)
    df = pd.read_parquet(inout.get_input_path(p))

    if pubs:
        p_pubs = 'ncbi/bioprojects/{}/pubs.parquet'.format(data_version)
        pubs_df = pd.read_parquet(inout.get_input_path(p_pubs))
    if authors:
        p_authors = 'ncbi/bioprojects/{}/authors.parquet'.format(data_version)
        authors_df = pd.read_parquet(inout.get_input_path(p_authors))

    if (pubs) and (authors):
        return df, pubs_df, authors_df
    elif pubs:
        return df, pubs_df
    elif authors:
        return df, authors_df
    else:
        return df


def gene_info(taxon_ncbi='all', usecols=None, mode=None):
    """
    Gene info file.

    Input:
    taxon_ncbi      'all' or int corresponding to ncbi_taxonomy identifier
    usecols         optional: list of columns to import
    mode            additional modes for preprocessing:
                    'unambiguous_ensembl': add gene_ensembl for 1:1
                    mapping with gene_ncbi

    """

    data_version = inout.get_data_version('gene_info')

    def _read_all(usecols):
        p = inout.get_input_path(
            'ncbi/data/{}/gene_info.parquet'.format(
                data_version)
        )
        df = pd.read_parquet(p, columns=usecols)
        return df

    if taxon_ncbi == 'all':
        df = _read_all(usecols)
    else:
        p = inout.get_input_path(
            'ncbi/data/{}/gene_info_{}.parquet'.format(
                data_version, int(taxon_ncbi))
        )
        if os.path.exists(p):
            df = pd.read_parquet(p, columns=usecols)
        else:
            df = _read_all(usecols)
            df = df[df['taxon_ncbi'] == taxon_ncbi]

    if mode == 'unambiguous_ensembl':
        helper = utils.stack_by_delimiter_in_column(
            df[['gene_ncbi', 'dbxrefs']].copy(),
            'dbxrefs', '|')

        helper = helper[helper['dbxrefs'].str.startswith('Ensembl:')]
        helper['gene_ensembl'] = helper['dbxrefs'].copy().apply(
            lambda x: x[len('Ensembl:'):])
        ncbi2ensembl = helper[['gene_ncbi', 'gene_ensembl']].drop_duplicates()

        c_ncbi = ncbi2ensembl['gene_ncbi'].value_counts()
        c_ensembl = ncbi2ensembl['gene_ensembl'].value_counts()

        ncbi2ensembl = ncbi2ensembl[
            ncbi2ensembl['gene_ncbi'].isin(c_ncbi[c_ncbi == 1].index) &
            ncbi2ensembl['gene_ensembl'].isin(c_ensembl[c_ensembl == 1].index)
            ]

        df = pd.merge(ncbi2ensembl, df)

    return df


def gene2go(taxon_ncbi='all', mask_non_supported=True):
    """
    Gene 2 GO file

    Input:
    taxon_ncbi      'all' or int corresponding to ncbi_taxonomy identifier
    """

    data_version = inout.get_data_version('gene2go')

    def _read_all():
        p = inout.get_input_path(
            'ncbi/data/{}/gene2go.parquet'.format(
                data_version)
        )
        df = pd.read_parquet(p)
        return df

    if taxon_ncbi == 'all':
        df = _read_all()
    else:
        p = inout.get_input_path(
            'ncbi/data/{}/gene2go_{}.parquet'.format(
                data_version, int(taxon_ncbi))
        )
        if os.path.exists(p):
            df = pd.read_parquet(p)
        else:
            df = _read_all()
            df = df[df['taxon_ncbi'] == taxon_ncbi]

    if mask_non_supported:
        forbidden_terms = df.loc[
            (
                df.loc[:, 'evidence'].isin(
                    ['ND'])
            ) | (
                df.loc[:, 'qualifier'].isin(
                    [
                        'NOT',
                        'NOT colocalizes_with',
                        'NOT contributes_to'
                    ])
            ),
            ['gene_ncbi', 'go_term']
        ]

        df = pd.merge(df, forbidden_terms, how='left', indicator=True)
        df = df.loc[
             df['_merge'] == 'left_only', :].drop('_merge', 1)

    return df


def gene2pubmed(taxon_ncbi='all'):
    """
    gene2pubmed file

    Input:
    taxon_ncbi      'all' or int corresponding to ncbi_taxonomy identifier
    """

    data_version = inout.get_data_version('gene2pubmed')

    def _read_all():
        p = inout.get_input_path(
            'ncbi/data/{}/gene2pubmed.parquet'.format(
                data_version)
        )
        df = pd.read_parquet(p)
        return df

    if taxon_ncbi == 'all':
        df = _read_all()
    else:
        p = inout.get_input_path(
            'ncbi/data/{}/gene2pubmed_{}.parquet'.format(
                data_version, int(taxon_ncbi))
        )
        if os.path.exists(p):
            df = pd.read_parquet(p)
        else:
            df = _read_all()
            df = df[df['taxon_ncbi'] == taxon_ncbi]

    return df


def generif(dataset):
    """
    geneRIFs

    Input:
    dataset         e.g.: generifs_basic
    """

    data_version = inout.get_data_version('generif')

    p = 'ncbi/gene/generif/{}/{}.parquet'.format(data_version, dataset)
    df = pd.read_parquet(inout.get_input_path(p))

    return df


def pubtator_articles(collection):
    """
    Loads articles from pubtator.

    Input:
    collection  name of pubtator collection, e.g.: covid19


    """

    data_version = inout.get_data_version('pubtator')

    p = inout.get_input_path(
        'ncbi/pubtator/{}/{}_articles.parquet'.format(data_version, collection)
    )
    df = pd.read_parquet(p)

    return df


def pubmed(dataset='main', columns=None, filters=None):
    """
    Loads pubmed

    dataset: 'main', 'mesh_terms', 'keywords', 'chemical_list', 'publication_types', 'funding', 'authors'
    columns: optional, list columns to load
    filters: optional dictionary, with column names as keys, and items being list of allowed
    """

    version = inout.get_data_version('pubmed')

    patch_pubdate_to_year = False
    if isinstance(columns, list):
        if 'year' in columns:
            patch_pubdate_to_year = True
            if 'pubdate' in columns:
                raise AssertionError(
                    'year and pubdate must not be defined at same time to avoid ambiguity'
                )

    if patch_pubdate_to_year:
        columns = [x.replace('year', 'pubdate') for x in columns]

    base_dir = inout.get_input_path('ncbi/pubmed/{}'.format(version))
    organizer = pd.read_parquet(os.path.join(base_dir, 'index.parquet'))

    agg = []
    for b in range(1, organizer['batch'].max() + 1):
        p = os.path.join(
            base_dir, 'batch_{:02d}_{}.parquet'.format(b, dataset))
        if os.path.exists(p):
            df = pd.read_parquet(p, columns=columns)
            
            if patch_pubdate_to_year:
                df = df.rename(columns={'pubdate': 'year'})
            
            if filters is not None:
                for key in filters.keys():
                    df = df.loc[df.loc[:, key].isin(filters[key]), :]
                    
            agg.append(df)

    df = pd.concat(agg)

   

    return df


def pubtator_medline(collection):
    """
    Loads a dataset from pubtator applied on medline from pubtator.

    Input:
    collection  name of pubtator collection, e.g.: pooled_counts_gene_unambiguous


    """

    data_version = inout.get_data_version('pubtator_medline')

    p = inout.get_input_path(
        'ncbi/pubtator_medline/{}/{}.parquet'.format(data_version, collection)
    )
    df = pd.read_parquet(p)

    return df


def pubtator_genes(collection):
    """
    Loads genes from pubtator.

    Input:
    collection  name of pubtator collection, e.g.: covid19


    """

    data_version = inout.get_data_version('pubtator')

    p = inout.get_input_path(
        'ncbi/pubtator/{}/{}_genes.parquet'.format(data_version, collection)
    )
    df = pd.read_parquet(p)

    return df


def pubtator_concepts(collection):
    """
    Loads concepts from pubtator.

    Input:
    collection  name of pubtator collection, e.g.: covid19


    """

    data_version = inout.get_data_version('pubtator')

    p = inout.get_input_path(
        'ncbi/pubtator/{}/{}_concepts.parquet'.format(data_version, collection)
    )
    df = pd.read_parquet(p)

    return df


def taxonomy(collection):
    """
    Loads NCBI taxonomy definitions

    Input:
    collection   names, nodes

    """

    data_version = inout.get_data_version('ncbi_taxonomy')

    p = inout.get_input_path(
        'ncbi/taxonomy/{}/{}.parquet'.format(data_version, collection)
    )
    df = pd.read_parquet(p)
    return df


def homologene():
    """
    Loads homologene

    Input:
    collection   names, nodes

    """

    data_version = inout.get_data_version('homologene')

    p = inout.get_input_path(
        'ncbi/homologene/{}/homologene.parquet'.format(data_version)
    )
    df = pd.read_parquet(p)
    return df
