import pandas as pd

from gustav import inout


def icite(dataset, columns=None):
    """
    iCite https://icite.od.nih.gov

    dataset: 'citations', 'citations_gene2pubmed',
             'studies', 'studies_gene2pubmed'

    columns: columns to load
    """

    data_version = inout.get_data_version('icite')

    p = inout.get_input_path(
        'nih/icite/{}/{}.parquet'.format(
            data_version, dataset)
    )
    df = pd.read_parquet(p, columns=columns)

    return df


def reporter(dataset, columns=None):
    """
    NIH reporter

    dataset: 'projects' (main funding information) or
             'publications_link' (links projects to pubmed_id)
             'abstracts' (of grants) or
             'patents' (resulting from grants) or
             'publications') (resulting from grant) or
             'clinical_studies' (resulting from grant)
    columns: columns to load
    """

    data_version = inout.get_data_version('reporter')

    p = inout.get_input_path(
        'nih/reporter/{}/{}.parquet'.format(
            data_version, dataset)
    )
    df = pd.read_parquet(p, columns=columns)

    return df
