import pandas as pd

from preparator import inout


def mesh():
    """
    Intrinsic information of MESH
    """

    data_version = inout.get_data_version('mesh')

    # Mapping to tree

    p = inout.get_input_path(
        'manual/nlm/mesh/{}/d2021.bin'.format(
            data_version))

    results = {}
    agg = []
    file1 = open(p, 'r')
    lines = file1.readlines()

    lines = [x.strip('\n') for x in lines]
    lines = pd.Series(lines)

    for line in lines:
        if line == '*NEWRECORD':
            agg.append(results)
            results = dict()
            results['MN'] = []
        if line.startswith('MN = '):
            results['MN'] = results['MN'] + [line[5:]]
        if line.startswith('UI = '):
            results['UI'] = line[5:]

    agg.append(results)

    used_keys = set()
    a = []

    for r in agg:
        if 'UI' in r.keys():
            ui = r['UI']

            if ui in used_keys:
                raise AssertionError('something wrong')
            else:
                used_keys.add(ui)

            if 'MN' in r.keys():
                if len(r['MN']) > 0:
                    h = pd.Series(r['MN']).to_frame('mn')
                    h.loc[:, 'ui'] = ui
                    a.append(h)

    u = pd.concat(a).reindex(columns=['ui', 'mn']).drop_duplicates()
    p = 'nlm/mesh/{}/ui2mn.parquet'.format(
        data_version)
    inout.export_plain_table(u, p)

    #### full tables #######

    tables = {
        'descriptor': 'd2021',
        'qualifier': 'q2021',
        'supplement': 'c2021'
    }

    for table in tables.keys():

        p = inout.get_input_path(
            'manual/nlm/mesh/{}/{}.bin'.format(
                data_version, tables[table]))
        results = {}
        agg = []
        file1 = open(p, 'r')
        lines = file1.readlines()

        lines = [x.strip('\n') for x in lines]
        lines = pd.Series(lines)

        lines = lines[lines != '']

        super_agg = []
        agg = []

        ix = 0
        for line in lines:
            if line == '*NEWRECORD':
                collection = pd.Series(agg, dtype=str).to_frame('line')

                if len(collection) > 0:
                    collection.loc[:, 'ix'] = ix
                    ix = ix + 1

                    super_agg.append(collection)

                agg = []

            else:
                agg.append(line)

        df = pd.concat(super_agg)

        df['qualifier'] = df['line'].str.extract('^(.*?) =')
        df['value'] = df['line'].str.extract('= (.*)$')

        patch = df[df['qualifier'] == 'UI'][['ix', 'value']].drop_duplicates()

        if any(patch['value'].duplicated()):
            raise AssertionError('Some unique identifier does not seem unique!')

        df = pd.merge(df, patch.rename(columns={'value': 'UI'}))

        df = df.reindex(columns=['UI', 'qualifier', 'value'])
        p = 'nlm/mesh/{}/{}.parquet'.format(
            data_version, table)
        inout.export_plain_table(df, p)

    return
