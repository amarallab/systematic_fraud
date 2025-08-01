import pandas as pd

from preparator import inout


def filtered_ch38():
    """
    Process filtered hit lists for GRCh38 provided on
    https://www.covid19hg.org/results/
    """

    data_version = inout.get_data_version('covid19hg')

    if data_version == '2020-07-01':

        datasets = {
            'very_severe_respiratory_confirmed_vs_population': 'COVID19_HGI_ANA_A2_V2_20200701.txt.gz_1.0E-5.txt',
            'hospitalized_covid_vs_not_hospitalized_covid': 'COVID19_HGI_ANA_B1_V2_20200701.txt.gz_1.0E-5.txt',
            'hospitalized_covid_vs_population': 'COVID19_HGI_ANA_B2_V2_20200701.txt.gz_1.0E-5.txt',
            'covid_vs_lab_or_self_reported_negative': 'COVID19_HGI_ANA_C1_V2_20200701.txt.gz_1.0E-5.txt',
            'covid_vs_population': 'COVID19_HGI_ANA_C2_V2_20200701.txt.gz_1.0E-5.txt',
            'predicted_covid_from_self_reported_symptoms_vs_predcited_or_self_reported_non_covid': 'COVID19_HGI_ANA_D1_V2_20200701.txt.gz_1.0E-5.txt',
        }

    elif data_version == '2020-10-12':

        datasets = {
            'very_severe_respiratory_confirmed_vs_population': 'COVID19_HGI_A2_ALL_20200930.txt.gz_1.0E-5.txt',
            'hospitalized_covid_vs_not_hospitalized_covid': 'COVID19_HGI_B1_ALL_20200930.txt.gz_1.0E-5.txt',
            'hospitalized_covid_vs_population': 'COVID19_HGI_B2_ALL_20200930.txt.gz_1.0E-5.txt',
            'covid_vs_lab_or_self_reported_negative': 'COVID19_HGI_C1_ALL_20200930.txt.gz_1.0E-5.txt',
            'covid_vs_population': 'COVID19_HGI_C2_ALL_20200930.txt.gz_1.0E-5.txt',
            'predicted_covid_from_self_reported_symptoms_vs_predcited_or_self_reported_non_covid': 'COVID19_HGI_D1_ALL_20200930.txt.gz_1.0E-5.txt',
        }

    for sheet in datasets.keys():
        p = inout.get_input_path(
            'manual/covid19hg/{}/{}'.format(data_version, datasets[sheet]))
        df = pd.read_csv(p, sep='\t')
        df = df[['SNP']]

        p = inout.get_intermediate_folder(
            'covid19hg/{}/{}.csv'.format(
                data_version, sheet)
        )
        inout.ensure_presence_of_directory(p)
        df.to_csv(p, index=False, header=False)

# def hgi_ana_a2_step1():

#     p = inout.get_input_path(
#         'manual/covid19hg/round_3/COVID19_HGI_ANA_A2_V2_20200629.txt.gz')
#     df = pd.read_csv(p, sep='\t')

#     significance = 5
#     df = df[df['all_inv_var_meta_p'] < 10**-significance]
#     df[['SNP']].to_csv(
#         '/Users/tstoeger/Desktop/example_gwas.txt', index=False, header=False)

#     p = inout.get_intermediate_folder(
#         'covid19hg/round_3/hgi_ana_a2_v2_meta_p_below_{}.csv'.format(
#             int(significance))
#     )
#     inout.ensure_presence_of_directory(p)
#     df.to_csv(p, index=False, header=False)
