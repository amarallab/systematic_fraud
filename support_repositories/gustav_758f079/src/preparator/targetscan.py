import pandas as pd

from preparator import inout


def targetscan():
    data_version = inout.get_data_version('targetscan')

    datasets = {
        'predicted_targets': 'Predicted_Targets_Info.default_predictions.txt',
        'predicted_targets_context_scores': 'Predicted_Targets_Context_Scores.default_predictions.txt',
        'gene_info': 'Gene_info.txt',
        'summary_counts_all': 'Summary_Counts.all_predictions.txt',
        'mir_family': 'miR_Family_Info.txt'
    }

    for table in datasets.keys():
        p = inout.get_input_path(
            'manual/targetscan/{}/{}'.format(
                data_version, datasets[table]
            ))

        df = pd.read_csv(p, sep='\t')
        df.columns = [x.lower().replace(' ', '_') for x in df.columns]

        df = df.rename(columns={
            'gene_id': 'gene_ensembl.version',
            'transcript_id': 'transcript_ensembl.version',
            'species_id': 'taxon_ncbi',
            'gene_tax_id': 'taxon_ncbi'
        })

        p = 'targetsan/data/{}/{}.parquet'.format(
            data_version, table)
        inout.export_plain_table(df, p)

    return
