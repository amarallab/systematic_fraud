import pandas as pd

from preparator import inout, served, mapper


def _lower_captions(df):
    df.columns = [x.lower() for x in df.columns]
    return df


def _mask_space(df):
    df.columns = [x.replace(' ', '_') for x in df.columns]
    return df


def blanco_melo_2020():
    """
    Extract differential gene expression following coronaviruses by
    Blanco Melo et al. 2020. Will pool data from cell culturs and
    primary cells to human_cells, and save clinical samples as
    human_patients
    """

    ncbi_gene_info = served.ncbi_gene_info(
        usecols=['taxon_ncbi', 'symbol_ncbi', 'gene_ncbi'])

    p = inout.get_input_path(
        'manual/publications/blanco_melo_2020/1-s2.0-S009286742030489X-mmc1.xlsx')
    df = pd.read_excel(p, sheet_name='DESeq2_Results')

    df_human_cell_lines = pd.merge(
        df.rename(columns={'GeneName': 'symbol_ncbi'}),
        ncbi_gene_info[ncbi_gene_info['taxon_ncbi'] == 9606][
            ['gene_ncbi', 'symbol_ncbi']]
    ).drop('symbol_ncbi', axis='columns').set_index(
        'gene_ncbi', verify_integrity=True).reset_index()

    p = inout.get_input_path(
        'manual/publications/blanco_melo_2020/1-s2.0-S009286742030489X-mmc2.xlsx')
    df = pd.read_excel(p, sheet_name='DESeq2_NHBECells')

    df_human_primary_cells = pd.merge(
        df.rename(columns={'GeneName': 'symbol_ncbi'}),
        ncbi_gene_info[ncbi_gene_info['taxon_ncbi'] == 9606][
            ['gene_ncbi', 'symbol_ncbi']]
    ).drop('symbol_ncbi', axis='columns').set_index(
        'gene_ncbi', verify_integrity=True).reset_index()

    df = pd.merge(
        df_human_cell_lines,
        df_human_primary_cells, indicator=True)

    if all(df['_merge'] == 'both'):
        df = df.drop('_merge', axis='columns')

    p = 'publications/blanco_melo_2020/human_cells.parquet'
    inout.export_plain_table(df, p)

    p = inout.get_input_path(
        'manual/publications/blanco_melo_2020/1-s2.0-S009286742030489X-mmc4.xlsx')
    df = pd.read_excel(p, sheet_name='DESeq2_COVID19 clinical samples')

    df = pd.merge(
        df.rename(columns={'Gene_name': 'symbol_ncbi'}),
        ncbi_gene_info[ncbi_gene_info['taxon_ncbi'] == 9606][
            ['gene_ncbi', 'symbol_ncbi']]
    ).drop('symbol_ncbi', axis='columns').set_index(
        'gene_ncbi', verify_integrity=True).reset_index()

    p = 'publications/blanco_melo_2020/human_patients.parquet'
    inout.export_plain_table(df, p)


def uhlen_2015():
    """
    FPKM expression levels as reported by 
    Uhlen et al. 2015
    """

    p = inout.get_input_path(
        'manual/publications/uhlen_2015/1260419__Excel_TablesS1-S18.xlsx')
    df = pd.read_excel(p, sheet_name='S18. Full FPKM dataset, tissues')
    df = df.rename(columns={'enstid': 'gene_ensembl'}
                   ).drop('gene_name', axis=1)

    df = _lower_captions(df)
    df = _mask_space(df)

    p = 'publications/uhlen_2015/tissues_ensembl.parquet'
    inout.export_plain_table(df, p)

    p = inout.get_input_path(
        'manual/publications/uhlen_2015/1260419__Excel_TablesS1-S18.xlsx')
    df = pd.read_excel(p, sheet_name='S11. FPKM Cell-lines')
    df = df.rename(columns={'enstid': 'gene_ensembl'}
                   ).drop('gene_name', axis=1)

    df.columns = [j.replace(
        '.MEAN', '') for j in df.columns]

    df = _lower_captions(df)
    df = _mask_space(df)

    df = df.rename(columns={'km3': 'reh'})

    p = 'publications/uhlen_2015/cells_ensembl.parquet'
    inout.export_plain_table(df, p)


def brehme_2014():
    """
    Extract chaperome definition from Brehme et al.,
    2014, Cell Reports
    """

    p = inout.get_input_path('manual/publications/brehme_2014/mmc3.xls')
    df = pd.read_excel(p, sheet_name='BREHME_TABLE S2A', header=8)
    df.columns = [x.lower() for x in df.columns]
    df = df.rename(columns={'entrez-id': 'gene_ncbi'})

    gi = served.ncbi_gene_info(['taxon_ncbi', 'gene_ncbi'])
    df = df[df['gene_ncbi'].isin(gi[gi['taxon_ncbi'] == 9606]['gene_ncbi'])]

    df = df.drop_duplicates()
    if df['gene_ncbi'].value_counts().max() > 1:
        raise AssertionError('Some genes appear duplicated')

    p = 'publications/brehme_2014/human.parquet'
    inout.export_plain_table(df, p)


def shemesh_2021():
    """
    Extract proteostasis definition from Shemesh et al.,
    2021, Nature communications
    """

    p = inout.get_input_path('manual/publications/shemesh_2021/41467_2021_22369_MOESM3_ESM.xlsx')
    df = pd.read_excel(p, header=2)
    df.columns = [x.lower() for x in df.columns]
    df = df.drop('name', axis=1).rename(columns={'ensg id': 'gene_ensembl'})

    df = mapper.gene_ensembl_2_gene_ncbi(df, taxon_ncbi=9606, unambiguous=True)
    df.columns = [x.replace('# ', 'nr ') for x in df.columns]

    df = df.drop_duplicates()
    if df['gene_ncbi'].value_counts().max() > 1:
        raise AssertionError('Some genes appear duplicated')

    p = 'publications/shemesh_2021/gene_list.parquet'
    inout.export_plain_table(df, p)


def karczewski_2020():
    """
    gnomAD data from Karczewski et al. 2020
    """

    p = inout.get_input_path(
        'manual/publications/karczewski_2020/supplementary_dataset_11_full_constraint_metrics.tsv.gz')

    df = pd.read_csv(p, sep='\t').rename(
        columns={
            'gene': 'symbol',
            'transcript': 'rna_ensembl'
        })

    df = _lower_captions(df)
    df = _mask_space(df)

    p = 'publications/karczewski_2020/full_constraint_metrics.parquet'
    inout.export_plain_table(df, p)


def jiang_2020():
    p = inout.get_input_path(
        'manual/publications/jiang_2020/1-s2.0-S0092867420310783-mmc3.xlsx')

    df = pd.read_excel(p, sheet_name='E protein tissue median', skiprows=2)
    df = df.rename(columns={'gene.id': 'gene_ensembl'})

    df = _lower_captions(df)
    df = _mask_space(df)

    p = 'publications/jiang_2020/tissue_median.parquet'
    inout.export_plain_table(df, p)


def partridge_2018():
    p = inout.get_input_path(
        'manual/publications/partridge_2018/table1_manually_digitalized_by_tstoeger.xlsx')
    df = pd.read_excel(p)
    df.columns = [
        x.replace('(s)', 's').replace('-', '_').replace(' ', '_').lower() for x in df.columns
    ]

    df['closest_genes'] = df['closest_genes'].replace(
        {'FOXO3A': 'FOXO3'}
    )

    p = 'publications/partridge_2018/gwas_loci.parquet'
    inout.export_plain_table(df, p)


def unnikrishnan_2018():
    p = inout.get_input_path(
        'manual/publications/unnikrishnan_2018/table_19_3_manually_extracted_by_tstoeger.xlsx')
    df = pd.read_excel(p)

    df = df[['symbol', 'gene_ncbi']].rename(columns={
        'symbol': 'label',
        'gene_ncbi': 'gene_ncbi_inferred_by_thomas_stoeger'
    }).drop_duplicates()

    p = 'publications/unnikrishnan_2018/table_19_3.parquet'
    inout.export_plain_table(df, p)
