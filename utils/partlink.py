
def using_partlink_data():
    
    from utils.connection import connection
    import pandas as pd
    from utils.queries import partlink
    from PROMSconfig import FROM_DATE, TO, TABLE, PUB_FILE_NAME

    #runs partlink script 
    cnxn = connection() #connects to sqlAlchemy
    data = pd.read_sql(partlink(FROM_DATE, TO, TABLE), cnxn)

    #converts number columns to number format
    for column in data.columns:
        try:
            data[column] = data[column].astype('float64')
        except ValueError:
            continue

    # removes england row in the data (as not needed for this)
    england_mask = data['Organisation Code'].isin(['England'])
    no_england_data=data[~england_mask]

    #selects only the organisation name column 
    no_england_data=no_england_data.sort_values(by=['Organisation Name - SC'])
    org_names = no_england_data['Organisation Name - SC']

    #adds data into correct sheets in excel
    with pd.ExcelWriter(PUB_FILE_NAME, engine='openpyxl', 
                        mode='a', if_sheet_exists='overlay') as writer:

        data.to_excel(writer, sheet_name='Participation - Raw Data', 
                        index=False, header=False, startrow=1)

        org_names.to_excel(writer, sheet_name='Reference', index=False, 
                            header=False, startcol=4, startrow=1)
