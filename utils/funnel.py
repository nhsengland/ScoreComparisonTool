
def using_funnel_data():

    from utils.connection import connection
    import pandas as pd
    from utils.queries import funneldata
    from PROMSconfig import TABLE, PUB_FILE_NAME, FYEAR, AGG_METHOD

    #runs funnel sql script
    cnxn3 = connection()
    funnel = pd.read_sql(funneldata(TABLE, FYEAR, AGG_METHOD), cnxn3)

    #converts number columns to number format
    for column in funnel.columns:
        try:
            funnel[column] = funnel[column].astype('float64')
        except ValueError:
            continue

    #writes to the excel file
    with pd.ExcelWriter(PUB_FILE_NAME, engine='openpyxl', 
                        mode='a', if_sheet_exists='overlay') as writer:

        funnel.to_excel(writer, sheet_name='Funnel setup', 
                        index=False, startcol=1, startrow=3, header=False)