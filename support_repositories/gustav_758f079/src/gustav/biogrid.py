import pandas as pd

from gustav import inout


def biogrid(dataset):
    """
    BioGRID (the protein interaction part of BioGRID)

    dataset: 'all' or 'coronavirus'
    """

    data_version = inout.get_data_version('biogrid')

    p = inout.get_input_path(
        'biogrid/biogrid/{}/{}.parquet'.format(
            data_version, dataset)
    )
    df = pd.read_parquet(p)

    return df


# def all():
#     """
#     BioGRID ALL collection: corresponds to full
#     BioGRID
#     """

#     data_version = inout.get_data_version('biogrid')

#     def _read_all():
#         p = inout.get_input_path(
#             'biogrid/biogrid/{}/biogrid_all.parquet'.format(
#                 data_version)
#         )
#         df = pd.read_parquet(p)
#         return df

#     df = _read_all()

#     return df


# def coronavirus():
#     """
#     BioGRID CORONAVIRUS collection
#     """

#     data_version = inout.get_data_version('biogrid')

#     def _read_all():
#         p = inout.get_input_path(
#             'biogrid/biogrid/{}/biogrid_coronavirus.parquet'.format(
#                 data_version)
#         )
#         df = pd.read_parquet(p)
#         return df

#     df = _read_all()

#     return df

def orcs(dataset):
    """
    Loads ORCS

    dataset: 'results', 'studies'
    """

    data_version = inout.get_data_version('biogrid_orcs')

    p = inout.get_input_path(
        'biogrid/orcs/{}/{}.parquet'.format(
            data_version, dataset)
    )

    df = pd.read_parquet(p)
    return df
