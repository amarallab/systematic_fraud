import pandas as pd

from gustav import inout


def agora():
    """
    Agora are the bona-fide Alzheimer's targets
    nominated by AMPAD
    
    Output:
    df   with bona-fide Alzheimer's targets
    """

    data_version = inout.get_data_version('ampad/agora')

    p = inout.get_input_path(
        'ampad/agora/{}/genes-list.parquet'.format(
            data_version)
    )
    df = pd.read_parquet(p)

    return df
