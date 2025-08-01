import pandas as pd

from preparator import inout


def maggiecrow_deprior():
    data_version = inout.get_data_version('deprior')

    p = inout.get_input_path(
        'manual/github/maggiecrow/deprior/{}/DE_Prior.txt'.format(
            data_version))

    df = pd.read_csv(p, sep='\t')

    df = df[['Gene_EntrezID', 'N_HitLists', 'DE_Prior_Rank']].rename(columns={
        'Gene_EntrezID': 'gene_ncbi',
        'N_HitLists': 'hit_lists',
        'DE_Prior_Rank': 'de_prior_rank'
    })

    df = df.set_index('gene_ncbi', verify_integrity=True).reset_index()

    p_out = 'github/maggiecrow/deprior/{}/de_prior.parquet'.format(
        data_version)
    inout.export_plain_table(df, p_out)


def gender_guesser():
    """
    Obtains gender frequencies on log2 scale, and parse
    them according to information in header of file.
    
    """

    data_version = inout.get_data_version('gender_guesser')

    p = inout.get_input_path(
        'manual/github/lead_ratings/gender_guesser/gender-guesser-0.4.0/gender_guesser/data/nam_dict.txt'.format(
            data_version))

    with open(p) as file:
        lines = file.readlines()

    agg = []
    for line in lines[293:]:
        agg.append([x for x in line])

    all_in = pd.DataFrame(agg)

    intensities = all_in.loc[:, 30: 84]

    intensities.columns = [x.strip('\n#$ ') for x in lines[108:273:3]]

    intensities = intensities.replace(
        {
            ' ': 0,
            'A': 10,
            'B': 11,
            'C': 12,
            'D': 13,
            #         'E': 14,
            #         'F': 15,
        }

    ).astype(int)

    agg = []
    for line in lines[293:]:
        agg.append(line[:3].strip())

    gender = pd.Series(agg)

    agg = []
    for line in lines[293:]:
        agg.append(line[3:29].strip())

    name = pd.Series(agg)

    together = pd.concat(
        [
            name.rename('first_name'),
            gender.rename('gender'),
            intensities

        ], axis=1

    )

    together = together.drop_duplicates()

    p_out = 'github/gender_guesser/{}/gender_frequencies.parquet'.format(
        data_version)
    inout.export_plain_table(together, p_out)
