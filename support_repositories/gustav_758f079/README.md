# gustav

Framework for extracting and organizing scientific data. Named after <a href="https://en.wikipedia.org/wiki/Gustav_Eisen">Gustav Eisen</a>, the unmet curator of biology

# How it works overall
- data from various sources
- src/preparator cleans and transforms these datasets
- and yields a curated version of the former data
- src/gustav then accesses this curated version
- By default will use versions of datasets as used by Stoeger et Amaral, Plos Biology 2022 (but this can be over-written as described in setup section)

# Setup - for people other than Thomas Stoeger
- get curated version of the former data (e.g.: link by Thomas Stoeger)
- copy gustav_TEMPLATE.csv to a subfolder called data_paths in your Documents folder, adjust content of gustav_TEMPLATE.csv and rename to gustav.csv (thus leaving something like HOME/Documents/data_paths/gustav.csv)
- optional: set custom versions of datasets to be used by placing a reference_data_custom.json file (you can use any other reference_data...json file as template) in main directory of repository
- note: usage of gustav only requires pandas, and for some data sets packages that are optional dependencies of pandas (such as for reading excel files or parquet files) whose absence will be indicated by pandas when needed. The underlying design consideration is to avoid unusual dependencies so that gustav can be used from custom environments that are tailored to different research needs and projects.

# Changing code

## Procedure 

- Thomas will generally try to maintain backwards compatibility
- If backwards compatibility will be broken, Thomas will release a release
- If you are not Thomas,  work on a separate branch and issue a merge request

## Conventions

### Storing
- strive for tables
- store tables in a way that would allow fast work when working with most/all records, but do not require all columns, e.g.: snappy-compressed parquet files

### Naming
- for genes and gene products: use the pattern "entity_source", e.g.: gene_ncbi, gene_ensembl, symbol_ncbi, transcript_ensembl, protein_uniprot; with symbol_official being special case to indicate that organisms specific official source of nomenclature (e.g.: HUGO for humans) was used for gene symbol
- for pubmed ids: use pubmed_id
- for years: use year

# Some datasets contained
- BioGRID: BioGRID interaction, ORCS screens
- Drugbank
- EBI: EGI-NHGRI GWAS catalog, EBI-GXA, Interpro, Uniprot
- NCBI: genes (incl. gene info, gene2pubmed, geneRIF), homologene, pubmed (all titles, abstracts, funding, MeSH keywords, etc....), PubTator, taxonomy
- NIH: iCite, reporter
- some more specialized ones

Note that Thomas additionally has some other collections of biology and bibliometrics, which together have most biological or bibliometric information (e.g.: all experimentallly verified chromatin binding experiments, or disambiguated authorship identifiers of scientists...)

