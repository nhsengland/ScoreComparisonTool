def using_provcomm_data():
    
    from utils.connection import connection
    import pandas as pd
    from utils.queries import provcomm
    from PROMSconfig import FROM_DATE, TO, TABLE, PUB_FILE_NAME, FYEAR

    # runs provcomm script
    cnxn2 = connection()
    providercomm = pd.read_sql(provcomm(FROM_DATE, TO, FYEAR, TABLE), cnxn2)
    providercomm.loc[providercomm['Organisation Code']=='R0D','Organisation Name'] = 'UNIVERSITY HOSPITAL DORSET NHS FUNDATION TRUST (R0D)'
    
    #converts number cells to number format rather than a string
    for i in providercomm.columns:
        for j in range(len(providercomm[i])):
            try:
                providercomm[i][j] = float(providercomm[i][j])
            except ValueError:
                continue
            except TypeError:
                continue
            
        
    #List of unique CCGs for Reference Tab
    ccg_mask = providercomm['Organisation Type'].isin(['CCG of GP Practice'])
    ccgs= providercomm[ccg_mask]
    unique_provs = ccgs.drop_duplicates(subset=['Organisation Name'])
    unique_provs.sort_values('Organisation Name')
    unique_provs = unique_provs['Organisation Name']

    #write things to correct excel sheets
    with pd.ExcelWriter(PUB_FILE_NAME,engine='openpyxl', mode='a', 
                        if_sheet_exists='overlay') as writer:

        providercomm.to_excel(writer, sheet_name='Provider Commission - Raw Data', 
                    index=False, startcol=2, startrow=1, header=False)

        providercomm.to_excel(writer, sheet_name='Provider Commission - NewChart', 
                    index=False, startcol=2, startrow=1, header=False)

        unique_provs.to_excel(writer, sheet_name='Reference', index=False, 
                                startcol=7, startrow=1, header=False)