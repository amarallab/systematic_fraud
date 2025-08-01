import pandas as pd

from gustav import inout


def gwas(dataset):
    """
    Obtain information on GWAS studies.

    Input:
        dataset  'associations', or 'studies'

    """

    data_version = inout.get_data_version('ebigwas')

    p = inout.get_input_path(
        'ebi/gwas/{}/{}.parquet'.format(
            data_version, dataset))

    df = pd.read_parquet(p)

    return df


def gxa(dataset, columns=None):
    """
    Obtain information on EBI-GXA studies.

    Input:
        dataset  'contrasts', 'de_all', 'studies', 'de_9606_entrez', "sample_info"
        columns   default: None (will load all);
                  optional: list of columns to import
        

    """

    data_version = inout.get_data_version('ebigxa')

    p = inout.get_input_path(
        'ebi/gxa/{}/{}.parquet'.format(
            data_version, dataset))

    df = pd.read_parquet(p, columns=columns)

    return df


def impc(dataset):
    """
    Obtain information from International Mouse
    Phenotyping Consortium.

    Input:
        dataset  'phenotype_hits_per_gene''

    """

    data_version = inout.get_data_version('impc')

    p = inout.get_input_path(
        'ebi/impc/{}/{}.parquet'.format(
            data_version, dataset))

    df = pd.read_parquet(p)

    return df



def uniprot(dataset, taxon_ncbi='vip'):
    """
    Loads uniprot datasets
    
    dataset   e.g.: uniprot_to_ncbi_gene
    taxon_ncbi  e.g.: vip
    
    
    """

    data_version = inout.get_data_version('uniprot')
    
    
    if dataset == 'uniprot_to_ncbi_gene':

        if taxon_ncbi == 'vip':
            p = inout.get_input_path(
                'ebi/uniprot/{}/protein_uniprot_to_gene_ncbi_vip_taxa.parquet'.format(
                data_version))
            df = pd.read_parquet(p)
            
        else: 
            raise AssertionError(
                'Provided value for taxon_ncbi not supported')
    
    else:
        
        raise AssertionError(
            'Dataset not implemented yet.')

    return df


