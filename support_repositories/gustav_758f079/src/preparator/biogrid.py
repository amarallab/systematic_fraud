import os

import numpy as np
import pandas as pd
from preparator import inout, served


def _lower_captions(df):
    df.columns = [x.lower() for x in df.columns]
    return df


def _load_biogrid_v3_file(path):
    """
    Loads a file in the biogrid Version 3 format, selects columns
    for subsequent work, avoiding ambiguities in used identifiers
    for genes and taxa, and ensuring consistent naming of columns
    stemming from different data sources. As the mapping of genes
    by BioGRID to taxa is inconsistent with NCBI's gene_info, which
    is authorative copy, mapping of taxa from BioGRID is replaced
    by the mapping from NCBI's gene_info

    Input:
        path     path to a biogrid file, in their version 3 formatting

    Output:
        df       dataframe containing interaction data

    """

    df = pd.read_csv(
        path,
        sep='\t',
        low_memory=False,
        usecols=[
            'Entrez Gene Interactor A', 'Entrez Gene Interactor B',
            # 'Organism Interactor A', 'Organism Interactor B',
            'Experimental System', 'Experimental System Type',
            'Author', 'Throughput',
            'Publication Source'
        ]
    ).rename(columns={
        'Entrez Gene Interactor A': 'gene_ncbi_interactor_A',
        'Entrez Gene Interactor B': 'gene_ncbi_interactor_B',
        # 'Organism Interactor A': 'taxon_ncbi_interactor_A',
        # 'Organism Interactor B': 'taxon_ncbi_interactor_B',
        'Experimental System': 'experimental_system',
        'Experimental System Type': 'experimental_system_type',
        'Author': 'author_year',
        'Throughput': 'throughput',
        'Publication Source': 'publication_source'
    }).reindex(columns=[
        'gene_ncbi_interactor_A', 'gene_ncbi_interactor_B',
        #         'taxon_ncbi_interactor_A', 'taxon_ncbi_interactor_B',
        'experimental_system', 'experimental_system_type',
        'author_year', 'throughput', 'publication_source'
    ])

    forbidden_interactors = ['-']
    c = ['gene_ncbi_interactor_A', 'gene_ncbi_interactor_B']
    has_forbidden = df.loc[:, c].isin(
        forbidden_interactors
    ).any(1)
    df = df.loc[~has_forbidden, :]
    df.loc[:, c] = df.loc[:, c].astype(int)

    df = df.drop_duplicates()
    df = _lower_captions(df)

    gene_2_taxon = served.ncbi_gene_info(['gene_ncbi', 'taxon_ncbi'])

    df = pd.merge(df, gene_2_taxon.rename(
        columns={
            'gene_ncbi': 'gene_ncbi_interactor_a',
            'taxon_ncbi': 'taxon_ncbi_interactor_a',
        }))

    df = pd.merge(df, gene_2_taxon.rename(
        columns={
            'gene_ncbi': 'gene_ncbi_interactor_b',
            'taxon_ncbi': 'taxon_ncbi_interactor_b',
        }))

    return df


def biogrid():
    """
    Processes the collections from BioGRID
    """

    data_version = inout.get_data_version('biogrid')
    
    
    paths = {
        'version_3_5_186': {
            'all': 'manual/biogrid/biogrid/version_3_5_186/BIOGRID-ALL-3.5.186.tab3.txt',
            'coronavirus': 'manual/biogrid/biogrid/version_3_5_186/BIOGRID-CORONAVIRUS-3.5.186.tab3.txt'
        },
        'version_4_4_215': {
            'all': 'manual/biogrid/biogrid/version_4_4_215/BIOGRID-ALL-4.4.215.tab3.txt',
            'coronavirus': 'manual/biogrid/biogrid/version_4_4_215/BIOGRID-CORONAVIRUS-4.4.215.tab3.txt'
        }
    }
    
    if data_version in paths.keys():
        current_paths = paths[data_version]
    else:
        raise ValueError(
            'Specified BioGrid version not supported.')
            
    for subset in current_paths.keys():

        p = inout.get_input_path(current_paths[subset])
        
        df = _load_biogrid_v3_file(p)

        
        p = 'biogrid/biogrid/{}/{}.parquet'.format(
            data_version, subset)
        inout.export_plain_table(df, p)
   
    return


# def covid_19():
#     """
#     Processes the CORONAVIRUS collection from BioGRID
#     """

#     data_version = inout.get_data_version('biogrid')

#     if data_version == 'version_3_5_186':
#         p = inout.get_input_path(
#             'manual/biogrid/version_3_5_186/BIOGRID-CORONAVIRUS-3.5.186.tab3.txt')
#     else:
#         raise ValueError('Specified BioGrid version not supported.')

#     df = _load_biogrid_v3_file(p)

#     p = 'biogrid/{}/biogrid_coronavirus.parquet'.format(
#         data_version)
#     inout.export_plain_table(df, p)

#     return

def orcs():
    """
    ORCS dataset of biogrid (CRISPR screens)
    """

    data_version = inout.get_data_version('biogrid_orcs')

    p_main = inout.get_input_path(
        'manual/biogrid/orcs/{}'.format(data_version)
    )

    column_renamer = {
        '#SCREEN_ID': 'orcs_screen_id',
        'ORGANISM_ID': 'taxon_ncbi',
    }

    # Load data
    agg_screens = []
    agg_index = []
    for animal_dir in [os.path.join(p_main, x) for x in os.listdir(p_main) if os.path.isdir(os.path.join(p_main, x))]:

        content = pd.Series(os.listdir(animal_dir))

        index = content[content.str.contains('^BIOGRID-ORCS-SCREEN_INDEX')]
        if len(index) != 1:
            raise AssertionError('Did not encoutner a single index file.')
        else:
            p = os.path.join(animal_dir, index.values[0])

        agg_index.append(pd.read_csv(p, '\t'))

        for screen in content[content.str.contains('^BIOGRID-ORCS-SCREEN_[0-9]+.*screen\.tab\.txt$')]:
            p = os.path.join(animal_dir, screen)

            if os.path.exists(p):
                agg_screens.append(pd.read_csv(p, '\t'))

    # export results
    df = pd.concat(agg_screens)

    df = df.drop(['OFFICIAL_SYMBOL', 'ALIASES', 'ORGANISM_OFFICIAL'], 1).rename(
        columns=column_renamer)

    if any(df['SOURCE'] != 'BioGRID ORCS'):
        raise AssertionError(
            'At least one source is not BioGRID ORCS. Have not programmed anticipation for this scenario.')
    else:
        df = df.drop('SOURCE', axis='columns')

    f = df['IDENTIFIER_TYPE'] == 'ENTREZ_GENE'
    df = df.loc[f, :].drop('IDENTIFIER_TYPE', axis='columns').rename(
        columns={'IDENTIFIER_ID': 'gene_ncbi'})

    if list(sorted(df['HIT'].unique())) != ['NO', 'YES']:
        raise AssertionError('Unexpected HITs')

    df['HIT'] = df['HIT'].replace({'YES': True, 'NO': False})

    df = df.set_index(['orcs_screen_id', 'taxon_ncbi',
                       'gene_ncbi', 'HIT']).reset_index()

    for x in [x for x in df.columns if x.startswith('SCORE')]:
        df.loc[:, x] = df.loc[:, x].replace('-', np.nan)

    df.columns = [x.lower() for x in df.columns]

    df['gene_ncbi'] = df['gene_ncbi'].astype(int)
    c = [x for x in df.columns if x.startswith('score')]
    df.loc[:, c] = df.loc[:, c].astype(float)

    p = 'biogrid/orcs/{}/results.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

    # export index with information on studies
    df = pd.concat(agg_index).rename(columns=column_renamer)

    df.columns = [x.lower() for x in df.columns]
    c = df.dtypes[df.dtypes == 'object'].index
    df.loc[:, c] = df.loc[:, c].astype(str)

    p = 'biogrid/orcs/{}/studies.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

    return
