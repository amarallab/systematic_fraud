import pandas as pd

from preparator import inout, served


def interpro_id_to_name():
    data_version = inout.get_data_version('interpro')

    p = inout.get_input_path(
        'manual/ebi/interpro/{}/protein2ipr.dat.gz'.format(
            data_version
        ),
        big=True
    )

    df = pd.read_csv(
        filepath_or_buffer=p,
        sep='\t',
        names=[
            'protein_uniprot',
            'interpro_id',
            'interpro_name',
            'external_id',
            'maybe_start',
            'maybe_stop'
        ],
        usecols=[
            'interpro_id',
            'interpro_name',
        ]
    ).drop_duplicates()

    p = 'ebi/interpro/{}/interpro_id_2_name.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

    return


def gene2domain():
    data_version = inout.get_data_version('interpro')

    p = inout.get_input_path(
        'manual/ebi/interpro/{}/protein2ipr.dat.gz'.format(
            data_version
        ),
        big=True
    )

    df = pd.read_csv(
        filepath_or_buffer=p,
        sep='\t',
        names=[
            'protein_uniprot',
            'interpro_id',
            'interpro_name',
            'external_id',
            'maybe_start',
            'maybe_stop'
        ],
        usecols=[
            'protein_uniprot',
            'interpro_id',
        ]
    ).drop_duplicates()

    mapper = served.uniprot_to_gene_ncbi('vip')

    taxa_of_interest = [9606, 7227, 10090, 6239]
    mapper = mapper[mapper['taxon_ncbi'].isin(taxa_of_interest)]

    d = pd.merge(mapper, df)
    d = d[['taxon_ncbi', 'gene_ncbi', 'interpro_id']].drop_duplicates()

    p = 'ebi/interpro/{}/gene2domain_vip_taxa.parquet'.format(
        data_version)
    inout.export_plain_table(d, p)

    return
