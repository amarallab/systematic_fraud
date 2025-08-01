import os
import urllib
import zipfile
from datetime import date

import pandas as pd
from preparator import inout, served, settings


def icite():
    """
    icite database on citation data

    """

    data_version = inout.get_data_version('icite')
    in_gene2pubmed = set(served.ncbi_gene2pubmed()['pubmed_id'])

    inserts = {
        'version_10': '12957656',
        'version_23': '16920079',
        'version_32': '20439960',
    }
    insert = inserts[data_version]

    p = inout.get_input_path(
        'manual/icite/{}/{}/open_citation_collection.csv'.format(
            data_version, insert),
        big=True
    )
    df = pd.read_csv(p)
    f = df.duplicated(df.columns)
    if any(f):
        raise AssertionError('Some columns are duplicated')
    p = 'nih/icite/{}/citations.parquet'.format(data_version)
    inout.export_plain_table(df, p)

    f = (df['citing'].isin(in_gene2pubmed)) & (
        df['referenced'].isin(in_gene2pubmed))
    df = df.loc[f, :]
    p = 'nih/icite/{}/citations_gene2pubmed.parquet'.format(data_version)
    inout.export_plain_table(df, p)

    # from tar file, which contains ~0.5% more records
    p = inout.get_input_path(
        'manual/icite/{}/{}/icite_metadata.csv'.format(data_version, insert),
        big=True
    )
    df = pd.read_csv(
        p,
        low_memory=False,
        usecols=[  # https://nih.figshare.com/collections/iCite_Database_Snapshots_NIH_Open_Citation_Collection_/4586573
            'pmid',
            'doi',
            'title',
            'authors',
            'year',
            'journal',
            'is_research_article',
            'citation_count',
            'field_citation_rate',
            'expected_citations_per_year',
            'citations_per_year',
            'relative_citation_ratio',
            'nih_percentile',
            'human',
            'animal',
            'molecular_cellular',
            #         'x_coord',
            #         'y_coord',
            'apt',
            'is_clinical',
            #         'cited_by_clin',
            #         'cited_by',
            #         'references',
            'provisional'
        ]
    )

    if list(sorted(df['provisional'].unique())) != ['No', 'Yes']:
        raise AssertionError('Unexpected provisional')

    df['provisional'] = df['provisional'].replace({'Yes': True, 'No': False})

    df.columns = [x.lower() for x in df.columns]
    c = df.dtypes[df.dtypes == 'object'].index
    df.loc[:, c] = df.loc[:, c].astype(str)

    df = df.rename(columns={'pmid': 'pubmed_id',
                            'provisional': 'rcr_is_provisional'})

    f = df.duplicated(df.columns)

    if any(f):
        raise AssertionError('Some columns are duplicated')

    f = df.duplicated(['pubmed_id'])

    if any(f):
        raise AssertionError('Some pubmed_ids are duplicated')

    p = 'nih/icite/{}/studies.parquet'.format(data_version)
    inout.export_plain_table(df, p)

    f = df['pubmed_id'].isin(in_gene2pubmed)
    df = df.loc[f, :]
    p = 'nih/icite/{}/studies_gene2pubmed.parquet'.format(data_version)
    inout.export_plain_table(df, p)


def exporter():
    today = date.today()
    data_version = today.strftime("%Y-%m-%d")

    download_settings = pd.DataFrame(
        settings.nih_exporter_settings
    ).transpose().rename_axis('dataset').reset_index()

    download_urls = []
    for _, r in download_settings.iterrows():

        # retreive settings
        url_scheme = r['url']
        increment_start = r['start']
        increment_end = r['end']

        # check how many characters (?) need to be replaced by increment
        if '?????' in url_scheme:
            raise AssertionError(
                'Unanticipated format. Maximally four ? signs supported.')
        elif '????' in url_scheme:
            characters_to_exchange = 4
        elif '???' in url_scheme:
            characters_to_exchange = 3
        elif '??' in url_scheme:
            characters_to_exchange = 2
        elif '?' in url_scheme:
            characters_to_exchange = 1
        else:
            characters_to_exchange = 0

        # Make list of files that need to be downloaded
        if characters_to_exchange == 0:
            record = {
                'category': r['category'],
                'download_url': url_scheme,
                'filename': os.path.split(url_scheme)[1]
            }
            download_urls.append(record)

        elif characters_to_exchange > 1:

            # convert (values need to be defined)
            increment_start = int(increment_start)
            increment_end = int(increment_end)

            # add individual increments to download list
            increment_range = range(increment_start, increment_end + 1)
            for i in increment_range:
                pattern_to_replace = '?' * characters_to_exchange
                pattern_of_increment = '{0:0>' + \
                                       str(characters_to_exchange) + '}'
                pattern_that_replaces = pattern_of_increment.format(i)
                download_url = url_scheme.replace(
                    pattern_to_replace, pattern_that_replaces)

                record = {
                    'category': r['category'],
                    'download_url': download_url,
                    'filename': os.path.split(download_url)[1]
                }

                download_urls.append(record)

        else:
            raise AssertionError('Unexpected number of characters')

    extended_organizer = pd.DataFrame(download_urls)

    # include safety check for the format, which was in use in October 2016 (namely zipped csv)
    if any(extended_organizer['download_url'].str.endswith('.zip') == False):
        raise AssertionError(
            'NIH has changed their format (Please update code to avoid errors.')

    cache_location = inout.get_intermediate_path(
        'nih/reporter/{}/'.format(data_version), big=True)
    inout.ensure_presence_of_directory(cache_location)

    extended_organizer['intermediate_raw'] = extended_organizer['filename'].apply(
        lambda x: os.path.join(cache_location, x))
    extended_organizer['intermediate_extracted'] = extended_organizer['intermediate_raw'].str.replace(
        'zip$', 'csv')

    extended_organizer.to_csv('~/Desktop/temporary_organizer.csv')

    print('Starting downloads.\r')

    for i, r in extended_organizer.iterrows():

        if os.path.exists(r['intermediate_extracted']):
            print('{}: Skipping download. Output file already present.'.format(
                r['intermediate_extracted']))
        else:
            urllib.request.urlretrieve(
                r['download_url'], r['intermediate_raw'])

            with zipfile.ZipFile(r['intermediate_raw']) as zf:
                for member in zf.infolist():
                    filename = member.filename.split('/')[0]
                    zf.extract(member, cache_location)

            # Clean up: remove originally downloaded zip file
            if os.path.exists(r['intermediate_extracted']):
                os.remove(r['intermediate_raw'])
            else:
                # e.g.: for RePORTER_PRJ_C_FY2019_new on 2020-11-03
                alternate = r['intermediate_extracted'].replace(
                    '.csv', '_new.csv')

                if os.path.exists(alternate):
                    extended_organizer.loc[i,
                                           'intermediate_extracted'] = alternate
                else:
                    raise AssertionError(
                        'Extraction of .zip file did not yield expected .csv')

        # Report progress of downloads to users
        if i % 10 == 0:
            t = len(download_urls)
            print('Finished processing of {} of {} downloads.\r'.format(i, t))

    # Report completion of processing of downloads to user
    print('Finished processing of all downloads.')

    def load_dataset(category):
        agg = []
        for fi in extended_organizer[
            extended_organizer['category'] == category]['intermediate_extracted']:

            #             print(fi)

            #             df = pd.read_csv(fi, low_memory=False, encoding='latin-1')

            header = pd.read_csv(fi, nrows=2, encoding='latin-1', low_memory=False).columns
            header = list(header) + ['to_discard']

            df = pd.read_csv(fi, names=header, encoding='latin-1', low_memory=False, skiprows=1)
            if df['to_discard'].isnull().all():
                df = df.drop(labels='to_discard', axis='columns')
            else:
                raise AssertionError(
                    'Unexpected formatting in {}'.format(fi))

            df = df.rename(
                columns={'PMID': 'pubmed_id'})
            # sometimes inconsistent across files for analogous columns
            df.columns = [x.lower() for x in df.columns]
            agg.append(df)

        df = pd.concat(agg)

        datatypes = pd.Series(df.dtypes)
        c = datatypes[datatypes == 'object'].index
        if len(c) > 0:
            df.loc[:, c] = df.loc[:, c].fillna('').astype(str)

        if category not in ['projects']:
            df = df.drop_duplicates()

        return df

    for category in extended_organizer['category'].unique():

        df = load_dataset(category)
        p_out = 'nih/reporter/{}/{}.parquet'.format(
            data_version, category)

        print('ongoing export:', category)
        if category == 'abstracts':
            inout.export_plain_table(df, p_out, params={'row_group_size': 100})
        else:
            inout.export_plain_table(df, p_out)
