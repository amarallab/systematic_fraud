priviledged_organisms = [
    9606,  # H. sapiens
    10090,  # M. musculus
    10116  # R. norvegicus
]

reference_data_versions = {
    'ampad/agora': '2021-08-16',
    'biogrid': 'version_4_4_215',
    'biogrid_orcs': 'version_1_1_13',
    'biosystems': 'rev22june2020',
    'bioprojects': '2021-04-01',
    'covid19hg': '2020-10-12',
    'dimensions_covid19': 'version_42',
    'deprior': '8bbb8a3',
    'depmap': 'depmap_20q2_public',
    'drugbank': 'v5_1_5',
    'ebigwas': '2022-08-17',
    'ebigxa': '2020-09-15',
    'gender_guesser': 'gender-guesser-0.4.0',
    'gene_info': '2022-08-16',
    'gene2go': '2022-08-16',
    'gene2pubmed': '2022-08-16',
    'generif': '2022-08-16',
    'hagr': '2020-12-21',
    'harmonizome': '2020-10-13',
    'homologene': 'build68',
    'human_protein_atlas': 'v20_1',
    'icite': 'version_32',
    'impc': 'release_17_0',
    'interpro': 'version_82',
    'mesh': '2020-12-28',
    'ncbi_taxonomy': '2022-08-16',
    'pubmed': '2021-12-17',
    'pubtator': '2021-11-09',  # COVID-19 collection
    'pubtator_medline': '2022-07-12',
    'targetscan': 'version_7_2',
    'uniprot': 'release_2022_03'
}

nih_exporter_settings = {
    'projects, prior years': {
        'url': 'https://exporter.nih.gov/CSVs/final/RePORTER_PRJ_C_FY????.zip',
        'category': 'projects',
        'start': '1985',
        'end': '2020'
    },
    'projects, last fiscal year': {
        'url': 'https://exporter.nih.gov/CSVs/final/RePORTER_PRJ_C_FY2021_???.zip',
        'category': 'projects',
        'start': '2',
        'end': '53'
    },
    'projects, current fiscal year': {
        'url': 'https://exporter.nih.gov/CSVs/final/RePORTER_PRJ_C_FY2022_???.zip',
        'category': 'projects',
        'start': '2',
        'end': '2'
    },
    'abstracts, prior years': {
        'url': 'https://exporter.nih.gov/CSVs/final/RePORTER_PRJABS_C_FY????.zip',
        'category': 'abstracts',
        'start': '1985',
        'end': '2020'
    },
    'abstracts, last fiscal year': {
        'url': 'https://exporter.nih.gov/CSVs/final/RePORTER_PRJABS_C_FY2021_???.zip',
        'category': 'abstracts',
        'start': '2',
        'end': '53'
    },
    'abstracts, current fiscal year': {
        'url': 'https://exporter.nih.gov/CSVs/final/RePORTER_PRJABS_C_FY2022_???.zip',
        'category': 'abstracts',
        'start': '2',
        'end': '2'
    },
    'publications': {
        'url': 'https://exporter.nih.gov/CSVs/final/RePORTER_PUB_C_????.zip',
        'category': 'publications',
        'start': '1980',
        'end': '2020'
    },
    'patents': {
        'url': 'https://exporter.nih.gov/CSVs/final/RePORTER_PATENTS_C_ALL.zip',
        'category': 'patents',
    },
    'clinical studies': {
        'url': 'https://exporter.nih.gov/CSVs/final/RePORTER_CLINICAL_STUDIES_C_ALL.zip',
        'category': 'clinical_studies'
    },
    'publications, link table': {
        'url': 'https://exporter.nih.gov/CSVs/final/RePORTER_PUBLNK_C_????.zip',
        'category': 'publications_link',
        'start': '1980',
        'end': '2020'
    }
}
