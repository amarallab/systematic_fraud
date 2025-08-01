import pandas as pd

from gustav import inout


def encode_tf_binding():
    df = _default_gene2annotation('encode_tf_binding')
    return df


def encode_histone_modifications():
    df = _default_gene2annotation('encode_histone_modifications')
    return df


def jaspar():
    df = _default_gene2annotation('jaspar')
    return df


def transfac_curated():
    df = _default_gene2annotation('transfac_curated')
    return df


def transfac_predicted():
    df = _default_gene2annotation('transfac_predicted')
    return df


def phosphositeplus_substrates_of_kinases():
    df = _default_gene2annotation('phosphositeplus_substrates_of_kinases')
    return df


def kea_substrates_of_kinases():
    df = _default_gene2annotation('kea_substrates_of_kinases')
    return df


def _default_gene2annotation(dataset):
    data_version = inout.get_data_version('harmonizome')
    p = inout.get_input_path(
        'harmonizome/{}/{}.parquet'.format(
            data_version, dataset))

    df = pd.read_parquet(p)
    return df
