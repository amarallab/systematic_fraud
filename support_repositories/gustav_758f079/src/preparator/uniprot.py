import pandas as pd

from preparator import inout, utils


def _lower_captions(df):
    df.columns = [x.lower() for x in df.columns]
    return df


def protein_uniprot_to_gene_ncbi():
    data_version = inout.get_data_version('uniprot')

    p = inout.get_input_path(
        'manual/ebi/uniprot/{}/idmapping_selected.tab.gz'.format(
            data_version
        ),
        big=True
    )

    df = pd.read_csv(
        p,
        sep='\t',
        names=[  # from README file, largely redundant with NIH gene info
            'UniProtKB-AC', 'UniProtKB-ID', 'GeneID (EntrezGene)', 'RefSeq',
            'GI', 'PDB', 'GO', 'UniRef100', 'UniRef90', 'UniRef50', 'UniParc',
            'PIR', 'NCBI-taxon', 'MIM', 'UniGene', 'PubMed', 'EMBL',
            'EMBL-CDS', 'Ensembl', 'Ensembl_TRS', 'Ensembl_PRO',
            'Additional PubMed'],
        usecols=['UniProtKB-AC', 'GeneID (EntrezGene)', 'NCBI-taxon'],
        low_memory=True,
        dtype={
            'UniProtKB-AC': str,
            'GeneID (EntrezGene)': str,
            'NCBI-taxon': int}).rename(columns={
        'UniProtKB-AC': 'protein_uniprot',
        'GeneID (EntrezGene)': 'gene_ncbi',
        'NCBI-taxon': 'taxon_ncbi'
    })

    df = df.dropna(subset=['gene_ncbi'])

    if df['protein_uniprot'].value_counts().max() > 1:
        raise AssertionError(
            'Mapping between uniprot and entrez genes is ambiguous')

    taxa_to_export = [9606, 10090, 6239, 7227]
    #     for taxon in taxa_to_export:

    d = df[df['taxon_ncbi'].isin(taxa_to_export)].copy()
    d = utils.stack_by_delimiter_in_column(d, 'gene_ncbi', '; ')

    #     return d

    d['gene_ncbi'] = d['gene_ncbi'].astype(int)
    d['protein_uniprot'] = d['protein_uniprot'].astype(str)
    d = d.drop_duplicates()

    p = 'ebi/uniprot/{}/protein_uniprot_to_gene_ncbi_vip_taxa.parquet'.format(
        data_version)
    inout.export_plain_table(d, p)

    return
