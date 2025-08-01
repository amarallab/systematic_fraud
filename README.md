# Code to accompany Richardson et al. (2025), "The entities enabling scientific fraud at scale are large, resilient, and growing rapidly" [https://doi.org/10.1073/pnas.2420092122](https://doi.org/10.1073/pnas.2420092122)

## Data availability

See **Materials and Methods** for descriptions of data sources. 

**Data, Materials, and Software Availability.** Code is available at [github.com/amarallab/systematic_fraud](https://github.com/amarallab/systematic_fraud) (98). Code for topic analyses is available at [github.com/amarallab/Science_fraud_topic_analysis](https://github.com/amarallab/Science_fraud_topic_analysis) (99). Some study data are available: All data presented in this work which is not under license from Clarivate (WoS,readers should wosg.support@clarivate.com for more details) or the PubPeer Foundation (readers should contact contact@pubpeer.com for more details) are available in [SI Appendix](https://www.pnas.org/lookup/doi/10.1073/pnas.2420092122#supplementary-materials). Historical data on indexing fromScopus (52), MEDLINE (53, 54), and OpenAlex (47) are publicly available.XML dumps from PLOS journals are publicly available (59). XML dumps fromHindawi journals were publicly available at the time of our analysis (60)but are no longer provided publicly by Wiley. Archives of the April 2, 2024,version of the dataset are available on Zenodo ([https://doi.org/10.5281/zenodo.13922491](https://doi.org/10.5281/zenodo.13922491)) (100) and Academic Torrents ([https://academictorrents.com/details/d402d0f51e2174d515b8a38d5af81478102a9f12](https://academictorrents.com/details/d402d0f51e2174d515b8a38d5af81478102a9f12)) (101).

# Directory of notebooks and their mapping to figures

Main text figures are preceded by F, supplementary figures are preceded by S. 

## analyze_allofhindawi.ipynb

Figures: S4, S5, S6, S7, S8, S9, S10, S11, S12, S13

Uses some data generated with: process_allofhindawi.ipynb

## analyze_allofplos.ipynb

Figures: F1, S2, S3

Uses some data generated with: process_allofplos.ipynb

## arda_timeline.ipynb

Figures: F3

## compare_flagging_models.ipynb

Figures: S25

Uses some data generated with: analyze_allofhindawi.ipynb, analyze_allofplos.ipynb

## ieee_conferences.ipynb

Figures: S14, S15

Uses some data generated with: openalex_summary_data.ipynb

## openalex_journal_rise_and_fall.ipynb

Figures: S16

Uses some data generated with: openalex_summary_data.ipynb, construct_paper_mill_corpus.ipynb

## openalex_summary_figures.ipynb

Figures: F5, S19, S20, S21, S22

Uses some data generated with: openalex_summary_data.ipynb, retraction_watch_timeseries.ipynb (batches in F5c), construct_paper_mill_corpus.ipynb

## paper_mill_retractions.ipynb

Figures: S23

Uses some data generated with: openalex_summary_data.ipynb, construct_paper_mill_corpus.ipynb

## patterns.ipynb

Figures: S24

## pubpeer_network.ipynb

Figures: F2

## semantic_distance.ipynb

Figures: S18

Uses some data generated with: process_plos.ipynb

# Notes

Figures F1E and S1 were generated and checked manually. Reproducing them requires knowledge of the identities of flagged authors and editors, which we did not want to declare publicly in our manuscript or code. The publicly-available [#allofplos dataset](https://plos.org/text-and-data-mining/) can be processed with process_allofplos.ipynb.

Code for reproducing F4 and S17 is available at [github.com/amarallab/Science_fraud_topic_analysis](https://doi.org/github.com/amarallab/Science_fraud_topic_analysis).

