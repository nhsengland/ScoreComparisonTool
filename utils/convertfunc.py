'''This is the collection of functions used to simplify repetitive sql query lines'''

def procedure_count(qh2proc,then,as_value):
    '''creates a string in the format: CONVERT(varchar, SUM(CASE WHEN QH2_Proc=''{qh2proc}'' then {then} else 0 end)) as ''{as_value}'', to use for repetitive sql queries '''

    return f''' CONVERT(varchar, SUM(CASE WHEN QH2_Proc=''{qh2proc}'' then {then} else 0 end)) as ''{as_value}'', '''


def remove_invalid_data(par1,column_name):
    '''creates a string in the format: case when {par1} in (''-999'',''-999.0000000'') then ''*'' else {par1} end as ''{column_name}'', to use for repetitive sql queries'''

    return f'''case when {par1} in (''-999'',''-999.0000000'') then ''*'' else {par1} end as ''{column_name}'', '''

new_table_columns = ['H3_Episodes','Q4_Q1Sent','QH5_PartRate','Q6_Q1Link','Q7_Linkrate',
                'Q8_Q2Sent','Q9_Q2IssRate','Q10_Q2Returned','Q11_Q2Resp']

procedure_count_all_procedures = [procedure_count('AllProc',column, f'AP_{index+1}' ) for index, column in enumerate(new_table_columns)]

procedure_count_HR = [procedure_count('HR',column, f'HR_{index+1}' ) for index, column in enumerate(new_table_columns)]

procedure_counts_HR_PRIM = [procedure_count('HR-PRIM',column, f'HR_PRIM_{index+1}' ) for index, column in enumerate(new_table_columns)]

procedure_counts_HR_REV = [procedure_count('HR-REV',column, f'HR_REV_{index+1}' ) for index, column in enumerate(new_table_columns)]

procedure_counts_KR = [procedure_count('KR',column, f'KR_{index+1}' ) for index, column in enumerate(new_table_columns)]

procedure_counts_KR_PRIM = [procedure_count('KR-PRIM',column, f'KR_PRIM_{index+1}' ) for index, column in enumerate(new_table_columns)]

procedure_counts_KR_REV = [procedure_count('KR-REV',column, f'KR_REV_{index+1}' ) for index, column in enumerate(new_table_columns)]

column_names_in_words_from_codes = ['Total HES Procedures','Total Pre-Op Qs','Participation Rate', 
                                    'Total Linked','Linkage rate','Total Q2s sent to date',
                                    'Issue rate','Total Q2s returned to date','Reponse rate']

invalid_data_all_procs = [remove_invalid_data(f'AP_{index+1}',f'All Procedures - {column}') 
                            for index,column in enumerate(column_names_in_words_from_codes)]
invalid_data_HR = [remove_invalid_data(f'HR_{index+1}',f'Hip Replacement - {column}') 
                            for index,column in enumerate(column_names_in_words_from_codes)]
invalid_data_HR_REV = [remove_invalid_data(f'HR_REV_{index+1}',f'Revision Hip Replacement - {column}') 
                            for index,column in enumerate(column_names_in_words_from_codes)]
invalid_data_KR = [remove_invalid_data(f'KR_{index+1}',f'Knee Replacement - {column}') 
                            for index,column in enumerate(column_names_in_words_from_codes)]
