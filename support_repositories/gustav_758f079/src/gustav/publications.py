import pandas as pd

from gustav import inout, mapper


def blanco_melo_2020(dataset):
    """
    Differntial gene expression for coronavirus as reported by
    Blanco Melo et al.

    Input:
        dataset     str: human_patients, or human_cells
    """

    if dataset == 'human_patients':
        p = 'publications/blanco_melo_2020/human_patients.parquet'
    elif dataset == 'human_cells':
        p = 'publications/blanco_melo_2020/human_cells.parquet'
    else:
        raise ValueError(
            'blanco_melo_2020 presently only supports human_patients and human_cells as inputs.'
        )

    df = pd.read_parquet(inout.get_input_path(p))
    return df


def brehme_2014(dataset='human'):
    """
    Data from Brehme et al. 2014, Cell Reports (chaperome)
    
    Input: 
    dataset  e.g.: human
    """

    p = 'publications/brehme_2014/{}.parquet'.format(dataset)
    df = pd.read_parquet(inout.get_input_path(p))
    return df


def shemesh_2021(dataset='gene_list'):
    """
    Data from Shemesh et al. 2021, Nature Communications
    (proteostasis genes)
    
    Input: 
    dataset  e.g.: gene_list
    """

    p = 'publications/shemesh_2021/{}.parquet'.format(dataset)
    df = pd.read_parquet(inout.get_input_path(p))
    return df


def uhlen_2015(dataset='tissues', to_ncbi='unambiguous', mode=None):
    """
    FPKM reported by Uhlen et al. 2015

    Input:
        dataset     str: 'tissues', or 'cells'
        to_ncbi     str: 'unambiguous'
        mode        e.g.: 'median' for tissue-medians
    """

    if dataset == 'tissues':
        p = 'publications/uhlen_2015/tissues_ensembl.parquet'
    else:
        raise ValueError(
            'uhlen_2015 presently only supports tissues as dataset.'
        )

    df = pd.read_parquet(inout.get_input_path(p)).set_index('gene_ensembl')

    if mode == 'median':
        df = df.transpose().rename_axis('sample').reset_index()
        df.loc[:, 'tissue'] = df['sample'].str.extract('^(.*)_', expand=False)
        df = df.drop('sample', axis=1)
        df = df.groupby('tissue').median().transpose()

    if to_ncbi == 'unambiguous':
        df = mapper.gene_ensembl_2_gene_ncbi(
            df, taxon_ncbi=9606, unambiguous=True)

    return df


def karczewski_2020(dataset, to_ncbi='unambiguous'):
    """
    Selection pressure

    Input:
        dataset     str: full_constraint_metrics
    """

    if dataset == 'full_constraint_metrics':
        p = 'publications/karczewski_2020/full_constraint_metrics.parquet'
    else:
        raise ValueError(
            'karczewski_2020 presently only supports full_constraint_metrics as dataset.'
        )

    df = pd.read_parquet(inout.get_input_path(p)).set_index('symbol')

    if to_ncbi == 'unambiguous':
        df = mapper.symbol_2_gene_ncbi(
            df, taxon_ncbi=9606, unambiguous=True)

    return df


def jiang_2020(dataset='tissue_median', to_ncbi='unambiguous'):
    """
    Tissue specific protein expression reported by Jiang
    et al. 2020

    Input:
    dataset     str: tissue_median
    to_ncbi     str: 'unambiguous'

    """

    if dataset == 'tissue_median':
        p = 'publications/jiang_2020/tissue_median.parquet'
    else:
        raise ValueError(
            'jiang_2020 presently only supports tissue_median as dataset.'
        )

    df = pd.read_parquet(inout.get_input_path(p)).set_index('gene_ensembl')

    if to_ncbi == 'unambiguous':
        df = mapper.gene_ensembl_2_gene_ncbi(
            df, taxon_ncbi=9606, unambiguous=True)

    return df


def partridge_2018(dataset):
    """
    Data from Partridge et al. 2018, Nature
    
    Input:
    dataset   str: gwas_loci
    
    """

    p = 'publications/partridge_2018/{}.parquet'.format(dataset)
    df = pd.read_parquet(inout.get_input_path(p))

    return df


def unnikrishnan_2018(dataset):
    """
    Data from Unnikrishnan et al.
    
    Input: 
    dataset  e.g.: table_19_3 for mouse genes with aging phenotypes
    """

    p = 'publications/unnikrishnan_2018/{}.parquet'.format(dataset)
    df = pd.read_parquet(inout.get_input_path(p))
    return df
