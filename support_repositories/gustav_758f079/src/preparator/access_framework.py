from access_biology_data import annotation, properties
from access_biology_data import lincs as access_lincs
from access_literature_data import wos, medline
from access_science_shared import inout as access_inout
from preparator import inout
from preparator import served, settings


import pandas as pd

def aminoacids_swissprot():
    data_version = access_inout.datasets['geisen']

    for taxon in settings.priviledged_organisms:
        df = properties.aminoacids_swissprot(taxon)
        df.columns = [x.replace('Aminoacids_swissprot: ', '') for x in df.columns]

        p = 'access_framework/{}/aminoacids_swissprot/{}.parquet'.format(
            data_version, int(taxon))
        inout.export_plain_table(df, p)


def aminoacids_trembl():
    data_version = access_inout.datasets['geisen']

    for taxon in settings.priviledged_organisms:
        df = properties.aminoacids_trembl(taxon)
        df.columns = [x.replace('Aminoacids_trembl: ', '') for x in df.columns]

        p = 'access_framework/{}/aminoacids_trembl/{}.parquet'.format(
            data_version, int(taxon))
        inout.export_plain_table(df, p)


def genbank_gene():
    data_version = access_inout.datasets['geisen']

    for taxon in settings.priviledged_organisms:
        df = properties.genbank_gene(taxon)
        df.columns = [x.replace('Genbank__gene: ', '') for x in df.columns]

        p = 'access_framework/{}/genbank_gene/{}.parquet'.format(
            data_version, int(taxon))
        inout.export_plain_table(df, p)


def predicted_cds_rna():
    data_version = access_inout.datasets['geisen']

    for taxon in settings.priviledged_organisms:
        df = properties.genbank_genomic_cds(taxon)
        df.columns = [x.replace('predicted_cds_rna_', '') for x in df.columns]

        p = 'access_framework/{}/predicted_cds_rna/{}.parquet'.format(
            data_version, int(taxon))
        inout.export_plain_table(df, p)


def predicted_genomic_rna():
    data_version = access_inout.datasets['geisen']

    for taxon in settings.priviledged_organisms:
        df = properties.genbank_genomic_rna(taxon)
        df.columns = [x.replace('predicted_genomic_RNA_', '') for x in df.columns]

        p = 'access_framework/{}/predicted_genomic_rna/{}.parquet'.format(
            data_version, int(taxon))
        inout.export_plain_table(df, p)


def genbank_validated_rna():
    data_version = access_inout.datasets['geisen']

    for taxon in settings.priviledged_organisms:
        df = properties.genbank_validated_rna(taxon)
        df.columns = [x.replace('Genbank_validated_RNA: ', '') for x in df.columns]

        p = 'access_framework/{}/genbank_validated_rna/{}.parquet'.format(
            data_version, int(taxon))
        inout.export_plain_table(df, p)


def lincs():
    """
    Datasets of LINCS 
    https://clue.io/connectopedia/perturbagen_types_and_controls
    """

    data_version = access_inout.datasets['lincs']

    df_genes = access_lincs.get_all_gene_meta()
    allowed_genes = list(served.ncbi_gene_info(
        usecols=['gene_ncbi'])['gene_ncbi'])

    df_cond = access_lincs.get_all_condition_meta()

    datasets = {  # there would be more datasets
        'consensus_short_hairpin': 'trt_sh.cgs',
        'overexpression': 'trt_oe'
    }

    for name in datasets.keys():

        dataset = datasets[name]

        values, _, _ = access_lincs.load_gene_perturbations(
            genes_exp=list(df_genes[df_genes['pr_is_lm'] == 1]['pr_gene_id']),
            genes_pert=allowed_genes,
            pert_type=[dataset]
        )

        values = values.transpose()

        p = 'access_framework/{}/{}/lm_genes_data.parquet'.format(
            data_version, name)
        inout.export_plain_table(values.reset_index(), p)

        if not all(values.columns.isin(df_cond['sig_id'])):
            raise AssertionError('Could not match to prospective meta.')

        meta = df_cond.copy().set_index('sig_id').reindex(list(values.columns))

        p = 'access_framework/{}/{}/lm_genes_meta.parquet'.format(
            data_version, name)
        inout.export_plain_table(meta.reset_index(), p)


def unified_disease():
    data_version = access_inout.datasets['geisen']

    df = annotation.disease_genealacart().drop_duplicates().replace(
        'No known disease', 'nothing reported'
    )

    p = 'access_framework/{}/unified_disease.parquet'.format(
        data_version)

    inout.export_plain_table(df, p)


def human_phenotype():
    data_version = access_inout.datasets['geisen']

    df = annotation.human_phenotype_genealacart().rename(
        columns={
            'human_phenotype_genealacart: human_phenotype_id': 'human_phenotype_id',
            'human_phenotype_genealacart: human_phenotype_name': 'human_phenotype_name'
        }
    ).drop_duplicates().replace(
        'No known human phenotype', 'nothing reported'
    )

    p = 'access_framework/{}/human_phenotype.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)


def orphanet():
    data_version = access_inout.datasets['geisen']

    df = annotation.orphanet_genealacart().drop_duplicates().replace(
        'No entry in Orphanet', 'nothing reported'
    )

    p = 'access_framework/{}/orphanet.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

    
    
    
def dais():
    data_version = access_inout.datasets['geisen']
    
    
    df = medline.select_medline_wos_records(
        columns_sql = '''
                medline.pubmed_id,
                ut2pmid.ut AS wos_id''',
        taxon_id = 'all',
        kind='research',
        unambiguous=True)

    dais = wos.dais('all')

    d = pd.merge(
        dais[['dais_id', 'wos_id', 'position']], 
        df
    )[['pubmed_id',  'dais_id', 'position']].drop_duplicates()
    d = d.sort_values(['pubmed_id', 'dais_id', 'position'])

    p = 'access_framework/{}/dais_research.parquet'.format(
        data_version)
    inout.export_plain_table(d, p)
    
    
    
    

