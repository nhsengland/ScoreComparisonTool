from utils.scoreComparison import produce_SC
 
'''
setting variables that change between each PROMs publication

'''

FYEAR = '2019'
FROM_DATE = '2019-04-01'
TO = '2020-03-31'
TABLE = '202012_V2_AR'
AGG_METHOD = 'Additive'
PUBLICATION_DATE = '11 February 2021'
PUBLICATION_LINK = 'http://digital.nhs.uk/pubs/promsapr20mar21fin'
PROV_PUBLICATION = 'FALSE' 
DATE_FINALIZED_PUBLICATION = 'February 2021'  
PUB_FILE_NAME = 'SCTool2019.xlsx'  


produce_SC()