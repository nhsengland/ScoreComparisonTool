from utils.partlink import using_partlink_data

def produce_SC():
    import pandas as pd
    import shutil
    from PROMSconfig import FYEAR, PUBLICATION_DATE, PUBLICATION_LINK, PROV_PUBLICATION, DATE_FINALIZED_PUBLICATION, PUB_FILE_NAME
    from utils.provcomm import using_provcomm_data
    from utils.funnel import using_funnel_data

    #duplicating template to use to add data
    shutil.copy('utils\\EmptySCTool.xlsx', PUB_FILE_NAME)

    using_partlink_data()
    using_provcomm_data()
    using_funnel_data()

    ## changes that dont come from an sql script 
    df = pd.DataFrame([f'April {FYEAR}', f'March {int(FYEAR)+1}', PUBLICATION_DATE, 
                        PROV_PUBLICATION, DATE_FINALIZED_PUBLICATION, '', PUBLICATION_LINK])

    with pd.ExcelWriter(PUB_FILE_NAME, engine='openpyxl', 
                        mode='a', if_sheet_exists='overlay') as writer:

        df.to_excel(writer, sheet_name='Reference', index=False, 
                    startcol=1, startrow=1, header=False)