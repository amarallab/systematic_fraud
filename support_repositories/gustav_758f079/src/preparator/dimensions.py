import os

import pandas as pd
from preparator import inout, utils


def covid_19_publications_datasets_and_clinical_trials():
    data_version = inout.get_data_version('dimensions_covid19')

    if data_version == 'version_24':
        p = inout.get_input_path(
            'manual/dimensions/covid_19_publications_datasets_and_clinical_trials/version_24/dimensions-covid19-export-2020_06_19_h10_50_00.xlsx')
    elif data_version == 'version_27':
        p = inout.get_input_path(
            'manual/dimensions/covid_19_publications_datasets_and_clinical_trials/version_27/dimensions-covid19-export-2020-07-03-h06-04-20.xlsx')
    elif data_version == 'version_33':
        p = inout.get_input_path(
            'manual/dimensions/covid_19_publications_datasets_and_clinical_trials/version_33/dimensions-covid19-export-2020-09-16-h06-08-18.xlsx')
    elif data_version == 'version_34':
        p = inout.get_input_path(
            'manual/dimensions/covid_19_publications_datasets_and_clinical_trials/version_34/dimensions-covid19-export-2020-10-16-h06-09-34.xlsx')
    elif data_version == 'version_37':
        p = inout.get_input_path(
            'manual/dimensions/covid_19_publications_datasets_and_clinical_trials/version_37/dimensions-covid19-export-2020-12-07-h06-13-08 (1).xlsx')
    elif data_version == 'version_42':
        p = inout.get_input_path(
            'manual/dimensions/covid_19_publications_datasets_and_clinical_trials/version_42')

    else:
        raise AssertionError('Provided data version not supported.')

    def _clean(df):
        df = df.rename(columns={
            'PMID': 'pubmed_id',
            'PMCID': 'pmc_id',
            'PubYear': 'pubdate_year',
            'Publication year': 'pubdate_year',
        })

        df = utils.lower_captions_and_replace_spaces(df)

        return df

    if data_version <= 'version_37':

        xl = pd.ExcelFile(p)
        sheets = xl.sheet_names

        for sheet in sheets:
            df = pd.read_excel(p, sheet_name=sheet)
            df = _clean(df)

            sheet = sheet.lower()
            sheet = sheet.replace(' ', '_')

            p_out = 'dimensions/covid_19_publications_datasets_and_clinical_trials/{}/{}.parquet'.format(
                data_version, sheet)
            inout.export_plain_table(df, p_out)

    else:
        for sheet in ['datasets', 'clinical_trials', 'grants', 'publications']:
            p_in = os.path.join(p, f'dimensions-covid19-export-2021-09-01-h15-01-02_{sheet}.csv')

            df = pd.read_csv(p_in, lineterminator='\n')
            df = _clean(df)

            p_out = 'dimensions/covid_19_publications_datasets_and_clinical_trials/{}/{}.parquet'.format(
                data_version, sheet)
            inout.export_plain_table(df, p_out)

    return
