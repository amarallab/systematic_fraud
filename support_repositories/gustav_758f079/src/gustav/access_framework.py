import pandas as pd

from gustav import inout


def lincs(dataset, scope='lm_genes'):
    """
    Data of LINCS
    
    Input:
        dataset  e.g.: consensus_short_hairpin,
                 overexpression
        scope    default: lm_genes
        
    Output:
        data
        meta
    
    """

    data_version = inout.get_data_version('access_framework_lincs')

    p = 'access_framework/{}/{}/{}_data.parquet'.format(
        data_version, dataset, scope)
    data = pd.read_parquet(inout.get_input_path(p))

    p = 'access_framework/{}/{}/{}_meta.parquet'.format(
        data_version, dataset, scope)
    meta = pd.read_parquet(inout.get_input_path(p))

    return data, meta


def unified_disease():
    data_version = inout.get_data_version('access_framework_geisen')

    p = 'access_framework/{}/unified_disease.parquet'.format(
        data_version)
    data = pd.read_parquet(inout.get_input_path(p))

    return data


def human_phenotype():
    data_version = inout.get_data_version('access_framework_geisen')

    p = 'access_framework/{}/human_phenotype.parquet'.format(
        data_version)
    data = pd.read_parquet(inout.get_input_path(p))

    return data


def orphanet():
    data_version = inout.get_data_version('access_framework_geisen')

    p = 'access_framework/{}/orphanet.parquet'.format(
        data_version)
    data = pd.read_parquet(inout.get_input_path(p))

    return data


def aminoacids_swissprot(taxon_ncbi):
    """
    Features on amino-acid composition for Swissprot proteins
    (which are the experimentally confirmed proteins in
    uniprot)
    
    Input:
        taxon_ncbi   int NCBI taxonomy identifier
    
    """

    data_version = inout.get_data_version('access_framework_geisen')

    p = 'access_framework/{}/aminoacids_swissprot/{}.parquet'.format(
        data_version, int(taxon_ncbi))
    data = pd.read_parquet(inout.get_input_path(p))

    return data


def aminoacids_trembl(taxon_ncbi):
    """
    Features on amino-acid composition for TREMBL proteins
    (which are the predicted proteins in
    uniprot)
    
    Input:
        taxon_ncbi   int NCBI taxonomy identifier
    
    """

    data_version = inout.get_data_version('access_framework_geisen')

    p = 'access_framework/{}/aminoacids_trembl/{}.parquet'.format(
        data_version, int(taxon_ncbi))
    data = pd.read_parquet(inout.get_input_path(p))

    return data


def genbank_gene(taxon_ncbi):
    """
    Features on nucleotide sequences for genes from genbank
    
    Input:
        taxon_ncbi   int NCBI taxonomy identifier
    
    """

    data_version = inout.get_data_version('access_framework_geisen')

    p = 'access_framework/{}/genbank_gene/{}.parquet'.format(
        data_version, int(taxon_ncbi))
    data = pd.read_parquet(inout.get_input_path(p))

    return data


def predicted_cds_rna(taxon_ncbi):
    """
    Features on coding sequences predicted by NCBI from RNA
    
    Input:
        taxon_ncbi   int NCBI taxonomy identifier
    
    """

    data_version = inout.get_data_version('access_framework_geisen')

    p = 'access_framework/{}/predicted_cds_rna/{}.parquet'.format(
        data_version, int(taxon_ncbi))
    data = pd.read_parquet(inout.get_input_path(p))

    return data


def predicted_genomic_rna(taxon_ncbi):
    """
    Features on native and mature RNA that is predicted by NCBI to exist
    
    Input:
        taxon_ncbi   int NCBI taxonomy identifier
    
    """

    data_version = inout.get_data_version('access_framework_geisen')

    p = 'access_framework/{}/predicted_genomic_rna/{}.parquet'.format(
        data_version, int(taxon_ncbi))
    data = pd.read_parquet(inout.get_input_path(p))

    return data


def genbank_validated_rna(taxon_ncbi):
    """
    Features on RNA that is flagged by NCBI to exist
    
    Input:
        taxon_ncbi   int NCBI taxonomy identifier
    
    """

    data_version = inout.get_data_version('access_framework_geisen')

    p = 'access_framework/{}/genbank_validated_rna/{}.parquet'.format(
        data_version, int(taxon_ncbi))
    data = pd.read_parquet(inout.get_input_path(p))

    return data



def dais(columns=None):
    """
    Load dais authorship identifiers mapped to pubmed (only
    for research publications, and unambiguous mapping
    of Web of Science IDs to pubmed)
    
    Input:
        columns   default: None (will load all columns)
    
    """

    data_version = inout.get_data_version('access_framework_geisen')

    p = 'access_framework/{}/dais_research.parquet'.format(
        data_version)
    data = pd.read_parquet(inout.get_input_path(p), columns=columns)

    return data
