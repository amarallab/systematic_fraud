import csv
import gzip
import json
import os
from os import listdir
from os.path import isfile, join

import numpy as np
import pandas as pd
import pubmed_parser as pp
import xmltodict
from preparator import inout, settings, served, utils


def _lower_captions(df):
    df.columns = [x.lower() for x in df.columns]
    return df


def bioprojects():
    data_version = inout.get_data_version('bioprojects')

    main_xml = inout.get_input_path(f'manual/ncbi/bioprojects/{data_version}/bioproject.xml')

    with open(main_xml, 'rb') as f:
        data_root = f.read()

    # ETA parsing time -- 7 mins
    data = xmltodict.parse(data_root, process_namespaces=True)

    del data_root

    data = data['PackageSet']['Package']

    # ETA loading time -- 20 mins
    df_projects = pd.json_normalize(data)

    del data

    renamer = {
        'Project.Project.ProjectID.ArchiveID.@accession': 'AccessionID',
        'Project.Project.ProjectID.ArchiveID.@archive': 'ArchiveName',
        'Project.Project.ProjectID.ArchiveID.@id': 'ArchiveID',
        'Project.Project.ProjectDescr.Name': 'ProjectName',
        'Project.Project.ProjectDescr.Title': 'ProjectTitle(Long)',
        'Project.Project.ProjectDescr.Description': 'ProjectDescription',
        'Project.Project.ProjectDescr.Publication': 'ProjectPublication',
        'Project.Project.ProjectDescr.ProjectReleaseDate': 'ProjectPublicRelease',
        'Project.Project.ProjectType.ProjectTypeSubmission.Target.@capture': 'ProjectFocus',
        'Project.Project.ProjectType.ProjectTypeSubmission.Target.@material': 'ProjectSampleMaterial',
        'Project.Project.ProjectType.ProjectTypeSubmission.Target.@sample_scope': 'ProjectScope',
        'Project.Project.ProjectType.ProjectTypeSubmission.Target.Organism.@taxID': 'TaxonomyID',
        'Project.Project.ProjectType.ProjectTypeSubmission.Target.Organism.OrganismName': 'TargetName',
        'Project.Project.ProjectType.ProjectTypeSubmission.Target.Organism.Strain': 'TargetStrain',
        'Project.Project.ProjectType.ProjectTypeSubmission.Target.Organism.Supergroup': 'TargetDomain',
        'Project.Project.ProjectType.ProjectTypeSubmission.Target.Organism.BiologicalProperties.Phenotype.Disease': 'DiseasePhenotype',
        'Project.Project.ProjectType.ProjectTypeSubmission.Target.Organism.GenomeSize.@units': 'GenomeSizeUnit',
        'Project.Project.ProjectType.ProjectTypeSubmission.Target.Organism.GenomeSize.#text': 'GenomeSizeCount',
        'Project.Project.ProjectType.ProjectTypeSubmission.Method.@method_type': 'MethodType',
        'Project.Project.ProjectType.ProjectTypeSubmission.Objectives.Data.@data_type': 'ObjectiveDataType',
        'Project.Project.ProjectType.ProjectTypeSubmission.ProjectDataTypeSet.DataType': 'ObjectiveDataTypeSet',
        'Project.Submission.@submitted': 'DateSubmitted',
        'Project.Submission.Description.Organization.@role': 'OrganizationRole',
        'Project.Submission.Description.Organization.@type': 'OrganizationType',
        'Project.Submission.Description.Organization.Name.@abbr': 'OrganizationNameAbbr',
        'Project.Submission.Description.Organization.Name.#text': 'OrganizationName',
        'Project.Project.ProjectDescr.Publication.@date': 'PublicationDate',
        'Project.Project.ProjectDescr.Publication.@id': 'PublicationID',
        'Project.Project.ProjectDescr.Publication.@status': 'PublicationStatus',
        'Project.Project.ProjectDescr.Publication.StructuredCitation.Title': 'PublicationTitle',
        'Project.Project.ProjectDescr.Publication.StructuredCitation.Journal.JournalTitle': 'PublicationJournal',
        'Project.Project.ProjectDescr.Publication.StructuredCitation.Journal.Year': 'PublicationYear',
        'Project.Project.ProjectDescr.Publication.StructuredCitation.AuthorSet.Author': 'PublicationAuthors',
        'Project.Project.ProjectDescr.Publication.DbType': 'PublicationDatabase'}

    df_projects = df_projects.rename(columns=renamer)

    # remove any entries that do not have an Archive ID (if it has an Archive ID, it has an Accession ID)
    df_projects = df_projects[df_projects.ArchiveID.notna()]

    df_projects = df_projects.reindex(columns=renamer.values())

    assert (len(df_projects.loc[(df_projects.PublicationID == None) & (df_projects.ProjectPublication == None)]) == 0), \
        'Every entry must contain either a single-publication entry or a nested publication entry. There exists entry(s) \
        that do not follow this rule.'

    # With these two assertions, we now can create two data clusters: one dataframe that holds all the submission/organism data and 
    # one json that contains all the publications/authors that are associated with the project
    # because every row contains a publication entry and an unique Accession/ArchiveID, we can link the two data clusters
    # with the ID numbers

    def process_pubs(row):
        publications = []

        if isinstance(row['ProjectPublication'], list) and isinstance(row['PublicationAuthors'], float):

            for onedict in row['ProjectPublication']:
                publication = {}
                title = None
                date = None
                pubid = None
                status = None
                database = None
                journaltitle = None
                journalyear = None
                consortium = None
                temp_name_list = []
                for key in onedict:
                    if '@date' in onedict:
                        date = onedict['@date']

                    if '@id' in onedict:
                        pubid = onedict['@id']

                    if '@status' in onedict:
                        status = onedict['@status']

                    if 'DbType' in onedict:
                        database = onedict['DbType']

                    if key == 'StructuredCitation':

                        if 'Title' in onedict[key]:
                            title = onedict[key]['Title']

                        if 'Journal' in onedict[key]:
                            if 'JournalTitle' in onedict[key]['Journal']:
                                journaltitle = onedict[key]['Journal']['JournalTitle']
                            if 'Year' in onedict[key]['Journal']:
                                journalyear = onedict[key]['Journal']['Year']

                        if 'Author' in onedict[key]['AuthorSet']:
                            for name in onedict[key]['AuthorSet']['Author']:
                                if isinstance(name, str):
                                    pass
                                else:
                                    if 'Consortium' in name:
                                        consortium = name['Consortium']

                                temp_name_list.append(name)

                        else:
                            temp_name_list.append([''])

                publication['title'] = title
                publication['date'] = date
                publication['id'] = pubid
                publication['status'] = status
                publication['database'] = database
                publication['journaltitle'] = journaltitle
                publication['journalyear'] = journalyear
                publication['authors'] = temp_name_list
                publication['consortium'] = consortium

                publications.append(publication)

        elif isinstance(row['ProjectPublication'], float) and isinstance(row['PublicationAuthors'], list):

            publication = {}
            temp_name_list = []
            consortium = None
            for name in row['PublicationAuthors']:
                if 'Consortium' in name:
                    consortium = name['Consortium']

                temp_name_list.append(name)

            publication['title'] = row['PublicationTitle']
            publication['date'] = row['PublicationDate']
            publication['id'] = row['PublicationID']
            publication['status'] = row['PublicationStatus']
            publication['database'] = row['PublicationDatabase']
            publication['journaltitle'] = row['PublicationJournal']
            publication['journalyear'] = row['PublicationYear']
            publication['authors'] = temp_name_list
            publication['consortium'] = consortium

            publications.append(publication)

        else:
            publications = None
        return publications

    df_projects['json'] = df_projects.apply(process_pubs, axis=1)

    pub_json = df_projects.set_index('AccessionID')['json'].to_dict()

    df_projects.drop(
        ['json', 'PublicationTitle', 'PublicationDate', 'PublicationID', 'PublicationStatus', 'PublicationDatabase' \
            , 'PublicationJournal', 'PublicationYear', 'PublicationAuthors', 'ProjectPublication'], inplace=True,
        axis=1)

    df_projects = df_projects.astype(str)

    # json_p = f'ncbi/bioprojects/{data_version}/bioprojects.json'
    # inout.export_plain_json(pub_json, json_p)

    pub_list = []
    pub_ids = []
    author_list = []
    author_ids = []
    len_nonames = 0
    for accession in sorted(pub_json):
        if pub_json[accession] != None:
            for i, pub in enumerate(pub_json[accession]):
                temp_pub = pub.copy()

                pub_id = accession + '_' + str(i)

                authors = temp_pub.pop('authors', None)

                if authors != None:
                    for author in authors:
                        if author != None:
                            try:
                                author_list.append(
                                    author['Name']
                                )
                                author_ids.append(pub_id)
                            except TypeError:
                                len_nonames += 1

                pub_list.append(pub)
                pub_ids.append(pub_id)

    author_df = pd.DataFrame({"authors": author_list, "pub_id": author_ids})
    pub_df = pd.DataFrame({"pubs": pub_list, "pub_id": pub_ids})

    pub_df_normal = pd.json_normalize(pub_df['pubs'])
    author_df_normal = pd.json_normalize(author_df['authors'])

    del pub_df['pubs']
    del pub_df_normal['authors']
    del author_df['authors']

    pub_df_normal.reset_index(inplace=True)
    pub_df.reset_index(inplace=True)
    merged_pub = pd.merge(pub_df, pub_df_normal, on='index')
    del merged_pub['index']

    author_df_normal.reset_index(inplace=True)
    author_df.reset_index(inplace=True)
    merged_author = pd.merge(author_df, author_df_normal, on='index')
    del merged_author['index']

    merged_pub['pubnumber'] = merged_pub['pub_id'].str.split('_').str[-1]
    merged_pub['pub_id'] = merged_pub['pub_id'].str.split('_').str[0]

    merged_author['pubnumber'] = merged_author['pub_id'].str.split('_').str[-1]
    merged_author['pub_id'] = merged_author['pub_id'].str.split('_').str[0]

    p = f'ncbi/bioprojects/{data_version}/bioprojects.parquet'
    inout.export_plain_table(df_projects, p)

    p_pubs = f'ncbi/bioprojects/{data_version}/pubs.parquet'
    inout.export_plain_table(merged_pub, p_pubs)

    p_authors = f'ncbi/bioprojects/{data_version}/authors.parquet'
    inout.export_plain_table(merged_author, p_authors)


def biosystems():
    data_version = inout.get_data_version('biosystems')

    p_gene = inout.get_input_path(
        'manual/ncbi/biosystems/{}/biosystems_gene.gz'.format(
            data_version))

    p_info = inout.get_input_path(
        'manual/ncbi/biosystems/{}/bsid2info.gz'.format(
            data_version))

    df_gene = pd.read_csv(
        p_gene,
        names=[  # From biosystems documentation (readme)
            'bsid_ncbi',
            'gene_ncbi',
            'score'],
        sep='\t',
        encoding='ISO-8859-1'
    )

    df_info = pd.read_csv(
        p_info,
        names=[  # From biosystems documentation (readme)
            'bsid_ncbi',
            'source database of biosystem',
            'source database accession',
            'name',
            'type of biosystem',
            'taxonomic scope of biosystem',
            'NCBI taxid',
            'description of biosystem'],
        sep='\t',
        encoding='ISO-8859-1'
    )

    # Create output
    df = pd.merge(
        df_gene,
        df_info,
        left_on='bsid_ncbi',
        right_on='bsid_ncbi',
        how='left')

    # Clean output
    c = ['bsid_ncbi', 'gene_ncbi', 'score', 'source database accession',
         'source database of biosystem', 'name', 'type of biosystem',
         'taxonomic scope of biosystem']
    f = df['source database of biosystem'].notnull()  # approx. 1%-2%
    df = df.loc[f, c]
    df = df.rename(columns={
        'score': 'bsid_2_gene_score',
        'source database accession': 'accession',
        'source database of biosystem': 'bsid_source',
        'name': 'biosystem_name',
        'type of biosystem': 'biosystem_type',
        'taxonomic scope of biosystem': 'biosystem_scope'
    })
    df = df.drop_duplicates(['bsid_ncbi', 'gene_ncbi'])

    gi = served.ncbi_gene_info(['gene_ncbi', 'taxon_ncbi'])

    df = pd.merge(gi, df)

    for taxon in settings.priviledged_organisms:
        p = 'ncbi/biosystems/{}/biosystems_{}.parquet'.format(
            data_version, int(taxon))
        inout.export_plain_table(df[df['taxon_ncbi'] == taxon], p)

    return


def gene_info():
    data_version = inout.get_data_version('gene_info')

    def _load_ncbi_gene_info_file(path):
        df = pd.read_csv(
            path, sep='\t',
            low_memory=False)
        df = df.rename(columns={
            '#tax_id': 'taxon_ncbi',
            'GeneID': 'gene_ncbi',
            'Symbol': 'symbol_ncbi',
        }).drop_duplicates()
        df = _lower_captions(df)
        return df

    p = inout.get_input_path(
        'manual/ncbi/gene/DATA/{}/gene_info.gz'.format(
            data_version
        ))
    df = _load_ncbi_gene_info_file(p)

    df = df[df['symbol_ncbi'] != 'NEWENTRY']
    df = df.drop_duplicates()

    p = 'ncbi/data/{}/gene_info.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

    for taxon in settings.priviledged_organisms:
        p = 'ncbi/data/{}/gene_info_{}.parquet'.format(
            data_version, int(taxon))
        inout.export_plain_table(df[df['taxon_ncbi'] == taxon], p)

    return


def gene2go():
    data_version = inout.get_data_version('gene2go')

    def _load_gene2go_file(path):
        """
        Loads an NCBI gene2go file

        Input:
            path     path to gene2go file

        Output:
            df       dataframe containing mapping to GO


        """

        df = pd.read_csv(path, sep='\t').rename(
            columns={
                '#tax_id': 'taxon_ncbi',
                'GeneID': 'gene_ncbi',
                'PubMed': 'pubmed_ids',
            }
        ).drop_duplicates()
        df = _lower_captions(df)

        return df

    p = inout.get_input_path(
        'manual/ncbi/gene/DATA/{}/gene2go.gz'.format(
            data_version
        ))
    df = _load_gene2go_file(p)
    df = utils.add_taxon_from_ncbi(df.drop('taxon_ncbi', axis='columns'))
    df = df.drop_duplicates()

    p = 'ncbi/data/{}/gene2go.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

    for taxon in settings.priviledged_organisms:
        p = 'ncbi/data/{}/gene2go_{}.parquet'.format(
            data_version, int(taxon))
        inout.export_plain_table(df[df['taxon_ncbi'] == taxon], p)

    return


def gene2pubmed():
    data_version = inout.get_data_version('gene2pubmed')

    def _load_ncbi_gene2pubmed_file(path):
        """
        Loads gene2pubmed, the mapping between genes and publications
        curated by the National Center for Biotechnology Information.
        Ensures consistent naming of columns stemming from different
        data sources.

        Input:
            path     path to gene2pubmed file

        Output:
            df       dataframe containing mapping of genes to pubmed

        """

        df = pd.read_csv(path, sep='\t').rename(
            columns={
                '#tax_id': 'taxon_ncbi',
                'GeneID': 'gene_ncbi',
                'PubMed_ID': 'pubmed_id'
            }
        )

        df = df.drop_duplicates()
        df = _lower_captions(df)

        return df

    p = inout.get_input_path(
        'manual/ncbi/gene/DATA/{}/gene2pubmed.gz'.format(
            data_version
        ))
    df = _load_ncbi_gene2pubmed_file(p)
    df = utils.add_taxon_from_ncbi(df.drop('taxon_ncbi', axis='columns'))
    df = df.drop_duplicates()

    # Add useful stat: attention, defined by 1/number of genes in publication
    df = pd.merge(
        df,
        (
                1 / df['pubmed_id'].value_counts()
        ).to_frame('attention').rename_axis('pubmed_id').reset_index()
    )

    p = 'ncbi/data/{}/gene2pubmed.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

    for taxon in settings.priviledged_organisms:
        p = 'ncbi/data/{}/gene2pubmed_{}.parquet'.format(
            data_version, int(taxon))
        inout.export_plain_table(df[df['taxon_ncbi'] == taxon], p)


def _load_pubtator_file(file_for_collection, data_version):
    if data_version >= '2021-11-09':  # manually decompressed as partial ambiguity in delimiters when gzip

        p = inout.get_input_path(
            'manual/ncbi/pubtator/{}/{}.json'.format(
                data_version, file_for_collection)
        )

        good = []
        bad = []
        ix = 1
        with open(p) as f:
            for line in f:
                if '{"_id"' in line:
                    good.append(line)
                else:
                    if ix <= 3:  # header
                        good.append(line)
                    elif line == ']]':
                        good.append(line)
                    else:
                        bad.append(line)
                #                         print(ix)
                ix = ix + 1

        print(len(bad), 'lines of ', (len(good) + len(bad)), 'lines could not be parsed.')

        p_intermediate = inout.get_intermediate_path('ncbi/pubtator/{}/{}.json'.format(
            data_version, file_for_collection))
        inout.ensure_presence_of_directory(p_intermediate)

        with open(p_intermediate, 'w') as f:  # write/read to file seems necessary to capture header
            f.writelines(good)

        with open(p_intermediate, 'r') as json_file:
            data = json.load(json_file)



    elif data_version >= '2021-02-17':  # manually decompressed as partial ambiguity in delimiters when gzip
        p = inout.get_input_path(
            'manual/ncbi/pubtator/{}/{}.json'.format(
                data_version, file_for_collection)
        )

        with open(p, 'r') as json_file:
            data = json.load(json_file)

    else:

        p = inout.get_input_path(
            'manual/ncbi/pubtator/{}/{}.json.gz'.format(
                data_version, file_for_collection)
        )

        with gzip.GzipFile(p, 'r') as json_file:
            data = json.load(json_file)

    header, data = data
    return data


def pubtator_medline_raw():
    version = inout.get_data_version('pubtator_medline')
    base_in = inout.get_input_path(
        'manual/ncbi/pubtator/{}'.format(version), big=True)


    if version >= '2022-07-12':

        files = [
            'gene2pubtatorcentral',
            'disease2pubtatorcentral',
            'chemical2pubtatorcentral',
            'species2pubtatorcentral',
            # 'mutation2pubtatorcentral',
            # 'cellline2pubtatorcentral'
        ]

        bad_files = []

    else:
        files = [
            'gene2pubtatorcentral',
            'chemical2pubtatorcentral',
            'species2pubtatorcentral',
                    # 'mutation2pubtatorcentral',
            'cellline2pubtatorcentral'
        ]

        bad_files = [  # has EOF character
            'disease2pubtatorcentral'
        ]



    
    for file in files:
        print(file)
        p_in = os.path.join(base_in, '{}.gz'.format(file))

        df = pd.read_csv(
            p_in,
            sep='\t',
            names=['pubmed_id', 'type', 'concept_id', 'mentions', 'resource'],
            low_memory=False
        )
        df['pubmed_id'] = df['pubmed_id'].astype(str)
        df['type'] = df['type'].astype(str)
        df['concept_id'] = df['concept_id'].astype(str)
        df['mentions'] = df['mentions'].astype(str)
        df['resource'] = df['resource'].astype(str)
        
        if df['type'].nunique() > 1:
            raise AssertionError('Type ambiguous for {}.'.format(
            file
            ))
        

        inout.export_plain_table(
            df,
            'ncbi/pubtator_medline/{}/{}.parquet'.format(version, file))

 
    if len(bad_files)>0:

        for file in bad_files:
            print(file)
            
            p_in = os.path.join(base_in, '{}.gz'.format(file))

            df = pd.read_csv(
                p_in,
                sep='\t',
                names=['pubmed_id', 'type', 'concept_id', 'mentions', 'resource'],
                quoting=csv.QUOTE_NONE, encoding='utf-8',
                low_memory=False
                #             quoting=3,
                #             error_bad_lines=False
            )
            df['pubmed_id'] = df['pubmed_id'].astype(str)
            df['type'] = df['type'].astype(str)
            df['concept_id'] = df['concept_id'].astype(str)
            df['mentions'] = df['mentions'].astype(str)
            df['resource'] = df['resource'].astype(str)
            
            if df['type'].nunique() > 1:
                raise AssertionError('Type ambiguous for {}.'.format(
                file
                ))
            
            inout.export_plain_table(
                df,
                'ncbi/pubtator_medline/{}/{}.parquet'.format(version, file))


def pubtator_medline_bioconcepts():
    version = inout.get_data_version('pubtator_medline')
    base = inout.get_input_path(
        'manual/ncbi/pubtator/{}'.format(version), big=True)

    if version >= '2022-01-23':
        file_extension = 'offset'
    else:
        file_extension = 'offset.gz'

    p_in = os.path.join(base, f'bioconcepts2pubtatorcentral.{file_extension}')

    #### Check whether there might be types that are wrong
    # in Jan-Mar 2022 some records were corrupted

    allowed = [
        'Cellline',
        'CellLine',
        'Chemical',
        'Disease',
        'Dnamutation',
        'Gene',
        'Genus',
        'Proteinmutation',
        'ProteinMutation',
        'Snp',
        'Species',
        'Strain',
        'SNP',
        'DNAmutation',
        'DNAMutation',
        'DomainMotif',
        'Chromosome',
        'GenomicRegion',
        'RefSeq',
        'DNAAcidChange',
        'CopyNumberVariant',
    ]

    agg_bad = []
    wrong_records = 0
    correct_records = 0
    for chunk in pd.read_csv(
        p_in,
        sep='\t',
        names=['text', 'start', 'end', 'mentions', 'type'],
        usecols=['type'],
        chunksize=10000000
    ):
        
        f = chunk['type'].isin(allowed)    
        if any(f):
            correct_records = correct_records + sum(f)
            
        f_w = ~f & chunk['type'].notnull()
        if any(f_w):
            wrong_records = wrong_records +  sum(f_w)
            d = chunk.loc[f_w, :]
            agg_bad.append(d.loc[:, ['type']])


    if wrong_records > 0:
        ch = pd.concat(agg_bad)
        ch = ch['type'].value_counts(dropna=False).to_frame('occurrences')
        display(ch)
        raise AssertionError('Some records appear corrupted')


    categories_to_process = [
        # 'Cellline',
        # 'CellLine',
        # 'Chemical',
        # 'Disease',
        # 'Dnamutation',
        'Gene',
        # 'Genus',
        # 'Proteinmutation',
        # 'ProteinMutation',
        # 'Snp',
        # 'Species',
        # 'Strain',
        # 'SNP',
        # 'DNAmutation',
        # 'DNAMutation',
        # 'DomainMotif',
        # 'Chromosome',
        # 'GenomicRegion',
        # 'RefSeq',
        # 'DNAAcidChange',
        # 'CopyNumberVariant',
    ]

    for category in categories_to_process:
        print('Processing: ', category)

        agg = []

        for chunk in pd.read_csv(
            p_in,
            sep='\t',
            names=['pubmed_id', 'start', 'end', 'mentions', 'type'],
            usecols=['pubmed_id', 'start', 'mentions', 'type'],
            chunksize=100000
        ):


            f = chunk['type'] == category
            if any(f):
                d = chunk.loc[f, :]
                
                d = d.drop('type', 1)
                d['pubmed_id'] = d['pubmed_id'].astype(int)
                d['start'] = d['start'].astype(int)
                d['mentions'] = d['mentions'].astype(str)

                agg.append(d)

        df = pd.concat(agg)

        if df.isnull().any().any():
            raise AssertionError(
                f'There is at least one absent value in {category}')

        inout.export_plain_table(
            df,
            'ncbi/pubtator_medline/{}/bioconcepts_{}.parquet'.format(
                version, category.lower()))






def pubtator_medline_cache_title_and_abstract():
    version = inout.get_data_version('pubtator_medline')

    base = inout.get_input_path(
        'manual/ncbi/pubtator/{}'.format(version), big=True)

    if version >= '2022-01-23':
        file_extension = 'offset'
    else:
        file_extension = 'offset.gz'
    p_in = os.path.join(base, f'bioconcepts2pubtatorcentral.{file_extension}')
    
    agg = []

    chunk_id = 0

    for chunk in pd.read_csv(
        p_in,
        sep='\t',
        names=['text', 'start', 'end', 'mentions', 'type'],
        usecols=['text', 'start'],
        chunksize=10000000
    ):
        f = chunk['text'].str.contains('^[0-9]*\|[at]\|')
        if any(f):            
            d = chunk.loc[f, :].copy()
            chunk_id = chunk_id+1
            
            if any(d['start'].notnull()):
                raise AssertionError('Unexpected')

            d['pubmed_id'] = d['text'].str.extract('^([0-9]+)\|[at]\|')
            d['digits'] = d['pubmed_id'].apply(lambda x: x[-3:])  
            
            
            d['section'] = d['text'].str.extract('^[0-9]+\|([at])\|')
            d['text'] = d['text'].str.extract('^[0-9]+\|[at]\|(.*)')

            d['text'] = d['text'].astype(str)
            d['section'] = d['section'].astype(str)
            d['pubmed_id'] = d['pubmed_id'].astype(int)

            d = d.pivot(index='pubmed_id', columns='section', values='text').rename(
                columns={'a': 'abstract', 't': 'title'}
            ).reset_index().fillna('')
            d.loc[:, 'abstract_length'] = d['abstract'].apply(lambda x: len(x))
            d.loc[:, 'title_length'] = d['title'].apply(lambda x: len(x))

            d = d.reset_index(drop=True)

            inout.export_plain_table(
                d,
                'ncbi/pubtator_medline/{}/text/text_{}.parquet'.format(
                    version, chunk_id),
                big=True,
                intermediate=True)


def pubtator_medline_count_annotations():
    trans = 'gene'
    version = inout.get_data_version('pubtator_medline')

    def get_lengths_of_title_and_abstract():
        collection = 'text'
        p = inout.get_intermediate_path(
            'ncbi/pubtator_medline/{}/{}'.format(version, collection), big=True)

        onlyfiles = [f for f in listdir(p) if isfile(join(p, f))]
        organizer = pd.Series(onlyfiles).to_frame('filename')

        pattern = collection + '_([0-9]+)\.parquet'
        organizer['batch'] = organizer['filename'].str.extract(pattern)

        organizer['path'] = organizer['filename'].apply(
            lambda x: os.path.join(p, x))

        agg = []
        for p in organizer['path'].unique():
            df = pd.read_parquet(
                p, columns=['pubmed_id', 'abstract_length', 'title_length'])
            agg.append(df)

        df = pd.concat(agg)
        df = df.rename(
            columns={
                'full_length': 'length_title_and_abstract',
                'title_length': 'length_title',
                'abstract_length': 'length_abstract'
            })

        return df

    p = inout.get_output_path(
        'ncbi/pubtator_medline/{}/bioconcepts_{}.parquet'.format(version, trans))
    trans_content = pd.read_parquet(p)

    text_content = get_lengths_of_title_and_abstract()

    text_content['length_title_and_abstract'] = text_content['length_abstract'] + \
                                                text_content['length_title']
    text_content = text_content[['pubmed_id',
                                 'length_title', 'length_title_and_abstract']]

    text_content = text_content[text_content['length_title'] > 0]

    master = pd.merge(trans_content, text_content)

    
    f = (master['start'] + 1) <= master['length_title'] # as of 2022-04-06 there are entities outside title/abstract
    master = master.loc[f, :]

    
    if not all((master['start'] + 1) <= master['length_title_and_abstract']):
        raise AssertionError('Out of expected bounds')

    gene2pc = pd.read_parquet(
        inout.get_output_path(
            'ncbi/pubtator_medline/{}/{}.parquet'.format(version, 'gene2pubtatorcentral'))
    ).rename(columns={'concept_id': 'gene_ncbi'})

    gene2pc = utils.stack_by_delimiter_in_column(gene2pc, 'mentions', '|')
    gene2pc = gene2pc[['pubmed_id', 'gene_ncbi', 'mentions']].drop_duplicates()

    gene2pc = gene2pc[~gene2pc['gene_ncbi'].isin(['nan', 'None'])].copy()
    gene2pc['pubmed_id'] = gene2pc['pubmed_id'].astype(int)

    for unambiguous in [False, True]:

        if unambiguous:
            gene2pc_helper = gene2pc[~gene2pc['gene_ncbi'].str.contains(
                ';')].copy()
            gene2pc_helper['gene_ncbi'] = gene2pc_helper['gene_ncbi'].astype(
                int)
        elif unambiguous == False:
            gene2pc_helper = gene2pc.copy()

        helper = pd.merge(master, gene2pc_helper)
        in_title = (helper['start'] + 1) <= helper['length_title']

        m = pd.merge(
            helper.loc[in_title, ['pubmed_id', 'start', 'gene_ncbi']].drop_duplicates().groupby(
                ['pubmed_id', 'gene_ncbi']).size().to_frame('bioconcept_title').reset_index(),
            helper[['pubmed_id', 'start', 'gene_ncbi']].drop_duplicates().groupby(
                ['pubmed_id', 'gene_ncbi']).size().to_frame('bioconcept_title_or_abstract').reset_index(),
            on=['pubmed_id', 'gene_ncbi'],
            how='outer'
        )

        m = pd.merge(
            m,
            gene2pc_helper[['pubmed_id', 'gene_ncbi']].drop_duplicates().groupby(
                ['pubmed_id', 'gene_ncbi']
            ).size().to_frame('gene2pubtatorcentral').reset_index(),
            on=['pubmed_id', 'gene_ncbi'], how='outer').fillna(0)

        m = pd.merge(m, text_content, how='left')

        m = pd.merge(
            m,
            helper[['pubmed_id', 'gene_ncbi', 'start']].drop_duplicates().sort_values('start').drop_duplicates(
                ['pubmed_id', 'gene_ncbi'], keep='first'
            ).rename(columns={'start': 'first_occurrence'}),
            how='left'
        )

        if unambiguous == True:
            p = 'ncbi/pubtator_medline/{}/pooled_counts_{}_unambiguous.parquet'.format(
                version, trans)
        elif unambiguous == False:
            p = 'ncbi/pubtator_medline/{}/pooled_counts_{}.parquet'.format(
                version, trans)

        inout.export_plain_table(m, p)


def pubtator_concepts(collection):
    """
    Obtains concepts in the COVID19 collection of pubtator

    """

    data_version = inout.get_data_version('pubtator')

    if collection == 'covid19':
        file_for_collection = 'litcovid2pubtator'
    else:
        raise AssertionError('specified collection not supported')

    data = _load_pubtator_file(file_for_collection, data_version)

    agg = []
    for article in data:

        for passage in article['passages']:

            if 'section_type' in list(passage['infons'].keys()):
                passage_type = passage['infons']['section_type']
            else:
                passage_type = 'absent_section_type'

            if 'type' in list(passage['infons'].keys()):
                part_type = passage['infons']['type']
            else:
                part_type = 'absent_type'

            if 'annotations' in passage.keys():
                annotations = passage['annotations']

                for annotation in annotations:
                    annotation = annotation

                    if 'infons' in annotation:
                        infons = annotation['infons']

                        record = {}
                        record['article_id'] = article['_id']
                        record['term_type'] = infons['type']
                        record['term_identifier'] = infons['identifier']
                        record['passage_type'] = passage_type
                        record['part_type'] = part_type
                        agg.append(record)

    df = pd.DataFrame(agg)

    f = (df['passage_type'] == 'absent_section_type') & (
            df['part_type'] == 'abstract')
    df.loc[f, 'passage_type'] = 'ABSTRACT'

    f = (df['passage_type'] == 'absent_section_type') & (
            df['part_type'] == 'title')
    df.loc[f, 'passage_type'] = 'TITLE'

    if any(df['passage_type'] == 'absent_section_type'):
        raise AssertionError(
            'At least one region could not be identified clearly')
    else:
        df = df[['article_id', 'passage_type', 'term_type', 'term_identifier', 'part_type']]

    helper = df[['article_id']].drop_duplicates()

    if not all(helper['article_id'].apply(lambda x: x.count('|')) == 1):
        raise AssertionError(
            """
            At least one record does not match the anticipated formatting for
            pubmed identifiers.
            """
        )
    else:

        helper['pubmed_id'] = helper['article_id'].str.extract('^(.*)\|').astype(float)
        helper['pmc_id'] = helper['article_id'].str.extract('^[0-9]+\|(.*)')

    df = pd.merge(df, helper)
    df = df.reindex(
        columns=[
            'pubmed_id', 'pmc_id', 'passage_type', 'part_type', 'term_type', 'term_identifier']
    ).drop_duplicates()

    p = 'ncbi/pubtator/{}/{}_concepts.parquet'.format(data_version, collection)
    inout.export_plain_table(df, p)


def pubtator_articles(collection):
    """
    Obtains articles in the COVID19 collection of pubtator

    """

    data_version = inout.get_data_version('pubtator')

    if collection == 'covid19':
        file_for_collection = 'litcovid2pubtator'
    else:
        raise AssertionError('specified collection not supported')

    data = _load_pubtator_file(file_for_collection, data_version)
    agg = []
    for article in data:
        article_id = article['_id']

        record = {}
        record['article_id'] = article_id
        agg.append(record)

    df = pd.DataFrame(agg)

    safety_check = []
    for j in df.index:
        m = df.loc[j, 'article_id']
        m = np.array([x == '|' for x in m])
        safety_check.append(m.sum() == 1)

    if all(safety_check):
        df['pubmed_id'] = df['article_id'].str.extract('^(.*)\|').astype(float)
        df['pmc_id'] = df['article_id'].str.extract('^[0-9]+\|(.*)')
        df = df.loc[:, ['pubmed_id', 'pmc_id']]
    else:
        raise AssertionError(
            """
            At least one record does not match the anticipated formatting for
            pubmed identifiers.
            """)

    df = df.drop_duplicates()

    p = 'ncbi/pubtator/{}/{}_articles.parquet'.format(data_version, collection)
    inout.export_plain_table(df, p)


def pubtator_genes(collection):
    """
    Obtains genes in the COVID19 collection of pubtator

    """

    data_version = inout.get_data_version('pubtator')

    if collection == 'covid19':
        file_for_collection = 'litcovid2pubtator'
    else:
        raise AssertionError('specified collection not supported')

    data = _load_pubtator_file(file_for_collection, data_version)

    agg = []
    for article in data:

        for passage in article['passages']:

            if 'section_type' in list(passage['infons'].keys()):
                passage_type = passage['infons']['section_type']
            else:
                passage_type = 'absent_section_type'

            if 'type' in list(passage['infons'].keys()):
                part_type = passage['infons']['type']
            else:
                part_type = 'absent_type'

            if 'annotations' in passage.keys():
                annotations = passage['annotations']

                for annotation in annotations:
                    annotation = annotation

                    if 'infons' in annotation:
                        infons = annotation['infons']
                        if infons['type'] == 'Gene':
                            record = {}
                            record['article_id'] = article['_id']
                            record['gene_ncbi'] = infons['identifier']
                            record['passage_type'] = passage_type
                            record['part_type'] = part_type
                            agg.append(record)

    df = pd.DataFrame(agg)

    f = (df['passage_type'] == 'absent_section_type') & (
            df['part_type'] == 'abstract')
    df.loc[f, 'passage_type'] = 'ABSTRACT'

    f = (df['passage_type'] == 'absent_section_type') & (
            df['part_type'] == 'title')
    df.loc[f, 'passage_type'] = 'TITLE'

    if any(df['passage_type'] == 'absent_section_type'):
        raise AssertionError(
            'At least one region could not be identified clearly')
    else:
        df = df[['article_id', 'passage_type', 'gene_ncbi']].rename(
            columns={'passage_type': 'section'})

    safety_check = []
    for j in df.index:
        m = df.loc[j, 'article_id']
        m = np.array([x == '|' for x in m])
        safety_check.append(m.sum() == 1)

    if all(safety_check):
        df['pubmed_id'] = df['article_id'].str.extract('^(.*)\|').astype(float)
        df['pmc_id'] = df['article_id'].str.extract('^[0-9]+\|(.*)')
        df = df.loc[:, ['pubmed_id', 'gene_ncbi', 'pmc_id', 'section']]
    else:
        raise AssertionError(
            """
            At least one record does not match the anticipated formatting for
            pubmed identifiers.
            """)

    df = utils.stack_by_delimiter_in_column(df, 'gene_ncbi', ';')
    f = df['gene_ncbi'] == 'None'
    df = df.loc[~f, :]
    df[['pubmed_id', 'gene_ncbi']] = df[[
        'pubmed_id', 'gene_ncbi']].astype(float)

    p = 'ncbi/pubtator/{}/{}_genes.parquet'.format(data_version, collection)
    inout.export_plain_table(df, p)


def taxdmp():
    data_version = inout.get_data_version('ncbi_taxonomy')

    def _read_ncbi_taxonomy_file(filepath, column_names):
        """
        Reads an ncbi taxonomy files (note which have unusual line breaks)
            filepath        path to taxonomy file
            column_names    list containing names of columns:
                            must be manually inferred from NCBI's documentation
                            (readme.txt on their server)
        """

        if not os.path.exists(filepath):
            raise EnvironmentError(
                'Could not find ' + filepath + ' . Please check spelling.\n')
        else:
            df = pd.read_table(
                filepath, sep='\t\|\t',
                header=None,
                names=column_names,
                engine='python')
            df[df.columns[-1]] = df[
                df.columns[-1]].map(lambda x: x.replace("\t|", ""))
        return df

    column_names = [  # from readme.txt:
        'tax_id',  # the id of node associated with this name
        'name_txt',  # name of taxon
        'unique name',  # the unique variant of this name if name not unique
        'name class']  # synonym, common name, ...

    p = inout.get_input_path(
        'manual/ncbi/pub/taxonomy/{}/taxdmp/names.dmp'.format(data_version))
    df = _read_ncbi_taxonomy_file(p, column_names)

    assert_df = df[df['name class'] == 'scientific name'].copy()
    if not all(assert_df['tax_id'].value_counts() == 1):
        raise AssertionError(
            'Scientific names are not unambiguous for individual taxon.' +
            'Please check if NIH changed format of files on their server')

    df = df.rename(columns={
        'tax_id': 'taxon_ncbi',
        'name_txt': 'taxon_name'})
    #     df = df.drop_duplicates('taxon_ncbi', keep=False)
    df = utils.lower_captions_and_replace_spaces(df)

    p = 'ncbi/taxonomy/{}/names.parquet'.format(data_version)
    inout.export_plain_table(df, p)

    p = inout.get_input_path(
        'manual/ncbi/pub/taxonomy/{}/taxdmp/nodes.dmp'.format(data_version))

    column_names = [  # from readme.txt
        'tax_id',  # node id in GenBank taxonomy database
        'parent tax_id',  # parent node id in GenBank taxonomy database
        'rank',  # superkingdom, kingdom, ...
        'embl code',  # locus-name prefix; not unique
        'division id',  # see division.dmp file
        'inherited div flag  (1 or 0)',  # inherits division from parent
        'genetic code id',  # see gencode.dmp file
        'inherited GC  flag  (1 or 0)',  # genetic code from parent
        'mitochondrial genetic code id',  # see gencode.dmp file
        'inherited MGC flag  (1 or 0)',  # mitochondrial gencode from parent
        'GenBank hidden flag (1 or 0)',  # suppressed in GenBank entry lineage
        'hidden subtree root flag (1 or 0)',  # no sequence data yet
        'comments']  # free-text comments and citations

    df = _read_ncbi_taxonomy_file(p, column_names)
    df = df.rename(columns={
        'tax_id': 'taxon_ncbi',
        'parent tax_id': 'parent_taxon_ncbi'
    })
    df = df.drop_duplicates('taxon_ncbi', keep=False)

    df = df.set_index('taxon_ncbi', verify_integrity=True).reset_index()
    df = utils.lower_captions_and_replace_spaces(df)

    p = 'ncbi/taxonomy/{}/nodes.parquet'.format(data_version)
    inout.export_plain_table(df, p)


def generif():
    data_version = inout.get_data_version('generif')

    p = inout.get_input_path(
        'manual/ncbi/gene/generif/{}/generifs_basic.gz'.format(
            data_version))

    df = pd.read_csv(
        p,
        sep='\t',
        low_memory=False
    )

    df = df.rename(columns={
        '#Tax ID': 'taxon_ncbi',
        'Gene ID': 'gene_ncbi',
        'PubMed ID (PMID) list': 'pubmed_ids',
        'last update timestamp': 'last_update',
        'GeneRIF text': 'text'
    }).drop_duplicates()

    p = 'ncbi/gene/generif/{}/generifs_basic.parquet'.format(
        data_version)
    inout.export_plain_table(df, p)

    return


def homologene():
    """
    Will download homologene from ncbi, and format it for further usage.
    Note that homologene maps can map the same gene to a different
    taxon, with MedLine usually showing the specific strain and
    homologene the taxonomy ID of the species
    - adhere to science of science naming conventions
    - map to taxonomy ID as used in Medline
    - remove entries / taxa that can not be mapped to Medline (note:
        if amount of genes is below a given threshold, default 100)
    - remove most meta-columns of homologene
    """

    # Setting: some genes in homologene do map to strain that
    # has not been used in MedLine -> require certain amount of
    # genes in homlologene to avoid keeping these taxa
    minimal_amount_of_required_genes = 100

    data_version = inout.get_data_version('homologene')

    p = inout.get_input_path(
        'manual/ncbi/pub/HomoloGene/{}/homologene.data.txt'.format(
            data_version
        ))

    df = pd.read_table(p, sep='\t', names=[
        'homologene_group', 'taxon_ncbi', 'gene_ncbi',
        'symbol_ncbi', 'prot_gi', 'protein_ncbi.version'])

    df = utils.add_taxon_from_ncbi(df.drop('taxon_ncbi', axis='columns'))
    df = df.drop_duplicates()

    genes_in_taxa = df['taxon_ncbi'].value_counts()
    allowed_taxa = genes_in_taxa[
        genes_in_taxa >= minimal_amount_of_required_genes].index

    df = df[df['taxon_ncbi'].isin(allowed_taxa)]
    df['taxon_ncbi'] = df['taxon_ncbi'].astype(int)
    df = df.loc[:, ['homologene_group', 'taxon_ncbi', 'gene_ncbi']]

    df = df.drop_duplicates()

    p = inout.get_output_path(
        'ncbi/homologene/{}/homologene.parquet'.format(data_version)
    )
    inout.export_plain_table(df, p)


def pubmed():
    batch_size = 25

    data_version = inout.get_data_version('pubmed')

    in_dir = inout.get_input_path(
        'manual/nlm/pubmed/baseline/{}'.format(data_version), big=True)
    out_subfolder = 'ncbi/pubmed/{}'.format(data_version)

    onlyfiles = [f for f in listdir(in_dir) if isfile(join(in_dir, f))]
    organizer = pd.Series(onlyfiles).to_frame('filename')
    f = organizer['filename'].str.contains('^pubmed.*\.xml\.gz$')
    organizer = organizer[f].sort_values(
        'filename').reset_index(drop=True).rename_axis('position').reset_index()
    organizer['batch'] = np.ceil((organizer['position'] + 1) / batch_size)
    organizer['batch'] = organizer['batch'].astype(int)

    p = os.path.join(out_subfolder, 'index.parquet')
    inout.export_plain_table(organizer, p)

    for batch in organizer['batch'].unique():

        #         print('Start processing batch', int(batch))
        files = list(organizer[organizer['batch'] == batch]['filename'].values)

        agg = []

        for file in files:
            p = os.path.join(in_dir, file)

            dict_out = pp.parse_medline_xml(
                p,
                nlm_category=False,
                author_list=True
            )
            agg.extend(dict_out)

        df = pd.DataFrame(agg).rename(columns={'pmid': 'pubmed_id'})

        df['pubdate'] = df['pubdate'].astype(int)
        df['pubmed_id'] = df['pubmed_id'].astype(int)

        c = [
            'title', 'abstract', 'journal', 'pubdate', 'pubmed_id',
            'doi',
            'delete', 'pmc', 'other_id', 'medline_ta',
            'nlm_unique_id', 'issn_linking', 'country']
        d = df.loc[:, c]
        p = os.path.join(
            out_subfolder, 'batch_{:02d}_main.parquet'.format(batch))
        inout.export_plain_table(d, p)

        agg = []
        df = df.reset_index(drop=True)

        for j in df.index:
            current = df.loc[j, 'authors']
            for x in current:
                r = x
                r['pubmed_id'] = df.loc[j, 'pubmed_id']
                agg.append(r)
        h = pd.DataFrame(agg)
        p = os.path.join(
            out_subfolder, 'batch_{:02d}_authors.parquet'.format(batch))
        inout.export_plain_table(h, p)

        for c in ['mesh_terms', 'publication_types', 'chemical_list', 'keywords']:
            d = df.loc[:, ['pubmed_id', c]]
            d = d[d.loc[:, c] != ''].copy()
            d = utils.stack_by_delimiter_in_column(d, c, '; ')

            p = os.path.join(
                out_subfolder, 'batch_{:02d}_{}.parquet'.format(batch, c))
            inout.export_plain_table(d, p)

        agg = []

        for file in files:
            p = os.path.join(in_dir, file)

            dict_out = pp.parse_medline_grant_id(
                p,
            )
            agg.extend(dict_out)

        df = pd.DataFrame(agg).rename(columns={'pmid': 'pubmed_id'})

        df['pubmed_id'] = df['pubmed_id'].astype(int)

        c = [
            'pubmed_id', 'country', 'agency', 'grant_acronym', 'grant_id']
        d = df.loc[:, c]
        p = os.path.join(
            out_subfolder, 'batch_{:02d}_funding.parquet'.format(batch))
        inout.export_plain_table(d, p)
