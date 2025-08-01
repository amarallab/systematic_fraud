import pandas as pd

from gustav import inout


def covid_19_publications_datasets_and_clinical_trials(sheet):
    """
    clinical_trials
    datasets
    grants
    publications
    """

    data_version = inout.get_data_version('dimensions_covid19')

    p = inout.get_input_path(
        'dimensions/covid_19_publications_datasets_and_clinical_trials/{}/{}.parquet'.format(
            data_version, sheet)
    )
    df = pd.read_parquet(p)

    return df
