library(biomaRt)

output_folder = '/Users/tstoeger/Dropbox/prepare_gustav/output/biomart/2020-04'


humanMart = useMart(
  host='http://apr2020.archive.ensembl.org',
  biomart = "ENSEMBL_MART_ENSEMBL",
  dataset =  "hsapiens_gene_ensembl"
) 


organism = 'csabaeus'

current_ortholog = paste0(organism, '_homolog_ensembl_gene')

orthologs = getBM(
  attributes = c("ensembl_gene_id", current_ortholog),
  mart = humanMart)

path_to_file = file.path(output_folder, paste0('homologs_', organism, '.csv'))
write.csv(orthologs, file= path_to_file, row.names=FALSE)

