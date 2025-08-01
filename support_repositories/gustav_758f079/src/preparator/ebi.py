import os
from os import listdir
from os.path import isfile, join, isdir

import pandas as pd
from preparator import inout, mapper, served, settings, utils


def _lower_captions(df):
    df.columns = [x.lower() for x in df.columns]
    return df


def impc():
    """
    Process data of the International Mouse
    Phenotyping Consortium
    """

    data_version = inout.get_data_version('impc')

    p = inout.get_input_path('manual/ebi/impc/{}/results/phenotypeHitsPerGene.csv.gz'.format(
        inout.get_data_version('impc')
    ))

    df = pd.read_csv(p)

    df = df.rename(columns={'Gene Symbol': 'symbol',
                            'Phenotype Hits': 'phenotype'})

    df = df[['symbol', 'phenotype']].dropna(subset=['symbol'])
    df['phenotype'] = df['phenotype'].fillna('none defined')

    df = utils.stack_by_delimiter_in_column(
        df, 'phenotype', '::').drop_duplicates()

    gi = served.ncbi_gene_info(
        usecols=['taxon_ncbi', 'gene_ncbi', 'symbol_ncbi'])
    gi = gi[gi['taxon_ncbi'] == 10090]

    df = pd.merge(gi.rename(columns={'symbol_ncbi': 'symbol'}), df)[
        ['gene_ncbi', 'phenotype']]

    p = 'ebi/impc/{}/phenotype_hits_per_gene.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)


def gwas():
    """
    Processes the EBI-NHGRI GWAS catalog
    """

    data_version = inout.get_data_version('ebigwas')

    if data_version == '2020-04-04':
        p_associations = inout.get_input_path(
            'manual/ebi/gwas/2020-04-04/full.tsv')
        p_studies = inout.get_input_path(
            'manual/ebi/gwas/2020-04-04/studies.tsv')
    elif data_version == '2021-05-19':
        p_associations = inout.get_input_path(
            'manual/ebi/gwas/{}/gwas-catalog-associations.tsv'.format(data_version))
        p_studies = inout.get_input_path(
            'manual/ebi/gwas/{}/gwas-catalog-studies.tsv'.format(data_version))
    elif data_version == '2022-02-20':
        p_associations = inout.get_input_path(
            'manual/ebi/gwas/{}/full'.format(data_version))
        p_studies = inout.get_input_path(
            'manual/ebi/gwas/{}/studies'.format(data_version))
    elif data_version == '2022-08-17':
        p_associations = inout.get_input_path(
            'manual/ebi/gwas/{}/full'.format(data_version))
        p_studies = inout.get_input_path(
            'manual/ebi/gwas/{}/studies'.format(data_version))
    else:
        raise AssertionError('data version not implemented')

    df = pd.read_csv(p_associations, sep='\t', low_memory=False).rename(columns={
        'PUBMEDID': 'pubmed_id'
    })
    df = _lower_captions(df)

    p = 'ebi/gwas/{}/associations.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

    df = pd.read_csv(p_studies, sep='\t').rename(columns={
        'PUBMEDID': 'pubmed_id'
    })
    df = _lower_captions(df)

    p = 'ebi/gwas/{}/studies.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

    return


def gxa():
    """
    Processing GXA atlas

    Code is largely ported from geisen_gxa
    """

    # Export GXA methods
    _gxa_methods()

    # Export GXA sample info (SDRF)
    _gxa_sample_info()

    # Export other GXA data
    data_version = inout.get_data_version('ebigxa')

    path_with_gxa = inout.get_input_path(
        'manual/ebi/gxa/{}/atlas-latest-data'.format(data_version), big=True)

    study_meta = _parse_all_idf_files(path_with_gxa)

    agg_genes, _, _, agg_contrasts = _parse_all_differential_expressions(
        path_with_gxa)

    df_genes = pd.concat(agg_genes, axis=0, ignore_index=True).rename(
        columns={'Gene ID': 'gene_ensembl'})
    df_genes = df_genes.loc[:, [
                                   'gene_ensembl',
                                   'log2foldchange',
                                   'p-value',
                                   'comparison_key']]

    df_contrasts = pd.DataFrame(
        agg_contrasts)
    df_contrasts = df_contrasts.loc[:, [
                                           'comparison_key',
                                           'experiment',
                                           'analysis',
                                           'comparison']].reset_index(drop=True)

    for j in df_contrasts.index:
        df_contrasts.loc[j, 'label'] = _get_from_config_file(
            path_with_gxa,
            df_contrasts.loc[j, 'experiment'],
            df_contrasts.loc[j, 'comparison'])

    p = 'ebi/gxa/{}/contrasts.parquet'.format(
        data_version)
    inout.export_plain_table(df_contrasts, p)

    p = 'ebi/gxa/{}/studies.parquet'.format(
        data_version)
    inout.export_plain_table(study_meta, p)

    p = 'ebi/gxa/{}/de_all.parquet'.format(
        data_version)
    inout.export_plain_table(df_genes, p)

    for taxon_ncbi in settings.priviledged_organisms:
        taxon_ncbi = int(taxon_ncbi)

        d = mapper.gene_ensembl_2_gene_ncbi(
            df_genes, taxon_ncbi=taxon_ncbi, unambiguous=True)
        p = 'ebi/gxa/{}/de_{}_entrez.parquet'.format(
            data_version, taxon_ncbi)
        inout.export_plain_table(d, p)


def _gxa_methods():
    data_version = inout.get_data_version('ebigxa')

    path_with_gxa = inout.get_input_path(
        'manual/ebi/gxa/{}/atlas-latest-data'.format(data_version), big=True)

    subfolders = [f for f in listdir(path_with_gxa) if isdir(join(path_with_gxa, f))]

    agg = []
    for subfolder in subfolders:

        p = os.path.join(path_with_gxa, subfolder)

        files = pd.Series([f for f in listdir(p) if isfile(join(p, f))])

        methods_files = files[files.str.contains('analysis[-_]methods\.tsv$')]

        if methods_files.shape[0] == 0:
            raise AssertionError('Did not find methods file')
        elif methods_files.shape[0] > 1:
            raise AssertionError('Multiple methods files appear present')

        path = os.path.join(p, list(methods_files)[0])
        df = pd.read_csv(path, sep='\t', names=['qualifier', 'value'])
        df.loc[:, 'experiment'] = subfolder
        df = df.reindex(columns=['experiment', 'qualifier', 'value'])
        agg.append(df)

    tf = pd.concat(agg)

    p = 'ebi/gxa/{}/analysis_methods.parquet'.format(
        data_version)
    inout.export_plain_table(tf, p)


def _gxa_sample_info():
    """
    Parses all SDRF files. These files appear to be proprietary
    format of EBI-GXA. 
    Output:
        stacked table containing:
        experiment       experimental ID
        platform	gene expression platform (e.g. A-AFFY-33)
        sample_name	name of sample/biological replicate
        value_type	"characteristic" or "factor"
        qualifier    e.g.: "age", "sex", "disease", etc.
        value        values for a given qualifier
        link	sometimes provides an external URL (for additional info on value)
    """

    data_version = inout.get_data_version('ebigxa')

    path_with_gxa = inout.get_input_path(
        'manual/ebi/gxa/{}/atlas-latest-data'.format(data_version), big=True)

    subfolders = [f for f in listdir(path_with_gxa) if isdir(join(path_with_gxa, f))]

    agg = []
    for subfolder in subfolders:

        p = os.path.join(path_with_gxa, subfolder)

        files = pd.Series([f for f in listdir(p) if isfile(join(p, f))])

        methods_files = files[files.str.contains('condensed[-_]sdrf\.tsv$')]

        if methods_files.shape[0] == 0:
            print(p)
            raise AssertionError('Did not find methods file')
        elif methods_files.shape[0] > 1:
            raise AssertionError('Multiple methods files appear present')

        path = os.path.join(p, list(methods_files)[0])
        df = pd.read_csv(path, sep='\t', header=None,
                         names=['experiment', 'platform', 'sample_name', 'value_type', 'qualifier', 'value', 'link'])
        df.loc[:, 'experiment'] = subfolder
        df = df.reindex(columns=['experiment', 'platform', 'sample_name', 'value_type', 'qualifier', 'value', 'link'])
        agg.append(df)

    tf = pd.concat(agg)

    tf = tf.fillna('').astype(str)

    p = 'ebi/gxa/{}/sample_info.parquet'.format(
        data_version)
    inout.export_plain_table(tf, p)


def _parse_all_idf_files(path_with_gxa):
    """
    Parses all IDF files. These files appear to be proprietary
    format of EBI-GXA. They contain meta-information about
    experiments, which is not biological (e.g.: email of authors,
    pubmed id of publication)

    Note that, besides parsing, no information is changed
    (e.g.: original empty values and vocabulary is maintained)

    Only considers records with at least two elements per record
    in the format of IDF e.g.: qualifer /tab something but not
    solely qualifer

    Output:
        stacked table containing:
        experiment       experimental ID
        qualifier    e.g.: "author first name" or "pubmed"
        value        values for a given qualifier
        position_in_record  starting with 1, the position if multiple
                            values for a record within a given experiment
    """

    agg_experiments = []
    paths = [f for f in listdir(path_with_gxa) if isdir(
        os.path.join(path_with_gxa, f))]

    for pe in paths:
        source = os.path.split(pe)[1]
        fname = os.path.join(path_with_gxa, source,
                             '{}.idf.txt'.format(source))

        if os.path.exists(fname):

            with open(fname, encoding='latin-1') as f:
                content = f.readlines()
            content = [x.strip() for x in content]

            agg = []
            for line in content:

                if line is not '':
                    elements = line.split('\t')
                    amount_of_elements = len(elements)

                    if amount_of_elements > 1:
                        to_process = range(1, amount_of_elements)
                        for j in to_process:
                            agg.append(
                                {
                                    'qualifier': elements[0],
                                    'value': elements[j],
                                    'position_in_record': j
                                })

            df = pd.DataFrame(agg)
            df.loc[:, 'experiment'] = source
            agg_experiments.append(df)

    d = pd.concat(agg_experiments).sort_values(
        ['experiment', 'qualifier', 'position_in_record']).reset_index(
        drop=True)[
        ['experiment', 'qualifier', 'value', 'position_in_record']
    ]

    return d


def _parse_all_differential_expressions(path_with_gxa):
    paths = [f for f in listdir(path_with_gxa) if isdir(
        os.path.join(path_with_gxa, f))]
    paths = [os.path.join(path_with_gxa, x) for x in paths]

    agg_genes = []
    current_comparison_key = 0
    agg_comparison_key = []
    agg_go = []
    agg_interpro = []

    for pe in paths:
        experiment = os.path.split(pe)[1]
        u = pd.Series(
            [f for f in listdir(pe) if os.path.isfile(os.path.join(pe, f))])
        pa = list(
            u[u.str.contains('{}[-_].*analytics.tsv$'.format(experiment))].values)
        pa = [os.path.join(pe, x) for x in pa]

        if len(pa) > 0:
            for paa in pa:  # sometimes there are several analyses

                df_genes = pd.read_table(paa, low_memory=False)

                _, current_analysis = os.path.split(paa)

                helper = pd.DataFrame(
                    data=df_genes.columns,
                    columns=['name'])
                comparisons = helper[helper['name'].str.endswith(
                    'log2foldchange')].loc[
                              :, 'name'].str.extract(
                    '^(.*)\.', expand=False).values

                for co in comparisons:
                    agg_comparison_key.append({
                        'comparison_key': current_comparison_key,
                        'experiment': experiment,
                        'comparison': co,
                        'analysis': current_analysis
                    })

                    usecols = [
                        'Gene ID',
                        '{}.log2foldchange'.format(co),
                        '{}.p-value'.format(co),
                    ]
                    dff = df_genes.loc[:, usecols]
                    dff = dff.rename(columns={
                        '{}.log2foldchange'.format(co): 'log2foldchange',
                        '{}.p-value'.format(co): 'p-value',
                    })

                    dff = dff.sort_values(
                        'p-value', ascending=True, na_position='last')

                    dff.loc[:, 'comparison_key'] = current_comparison_key
                    agg_genes.append(dff)

                    #                     p_go = os.path.join(
                    #                         pe, '{}.{}.go.gsea.tsv'.format(
                    #                             experiment,
                    #                             co))
                    #                     if os.path.exists(p_go):
                    #                         contains_data, df = _read_go_or_interpro(p_go)
                    #                         if contains_data:
                    #                             df.loc[
                    #                                 :, 'comparison_key'] = current_comparison_key
                    #                             agg_go.append(df)

                    #                     p_interpro = os.path.join(
                    #                         pe, '{}.{}.interpro.gsea.tsv'.format(
                    #                             experiment,
                    #                             co))
                    #                     if os.path.exists(p_interpro):
                    #                         contains_data, df = _read_go_or_interpro(p_interpro)
                    #                         if contains_data:
                    #                             df.loc[
                    #                                 :, 'comparison_key'] = current_comparison_key
                    #                             agg_interpro.append(df)

                    current_comparison_key += 1

    return agg_genes, agg_go, agg_interpro, agg_comparison_key


def _get_from_config_file(path_with_gxa, experiment, comparison):
    """
    Obtains experimental design from experimental configuration
    file within an comparison.
    """

    p = os.path.join(
        path_with_gxa, '{0}/{0}-configuration.xml'.format(experiment))

    condition_was_found = False

    if os.path.isfile(p):

        with open(p, 'r') as file:
            config_file = file.readlines()

        config_file = [x.strip() for x in config_file]

        watch_next = False

        for line in config_file:
            if watch_next:
                if condition_was_found:  # robust against source duplications
                    raise ValueError('Assumption of T. Stoeger not correct')
                else:
                    condition_was_found = True
                    label = line.replace(
                        "<name>", '').replace(
                        "</name>", '').replace(
                        "'", '').replace(
                        ' vs ', ' VS ')

            if line.startswith('<contrast id="{}" '.format(comparison)):
                watch_next = True
            elif line.startswith('<contrast id="{}">'.format(comparison)):
                watch_next = True
            else:
                watch_next = False

    if not condition_was_found:
        label = ''

    return label
