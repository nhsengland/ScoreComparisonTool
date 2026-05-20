def partlink(fromDate, to, table):
    '''creates the string for the sql participation linkage query, inserting the variables into it'''
    from utils.convertfunc import procedure_count_all_procedures,procedure_count_HR,procedure_counts_HR_PRIM,procedure_counts_HR_REV,procedure_counts_KR,procedure_counts_KR_PRIM,procedure_counts_KR_REV,invalid_data_all_procs,invalid_data_HR, invalid_data_HR_REV,invalid_data_KR


    partlinkStr = (f'''DECLARE @from DATE = '{fromDate}'
        DECLARE @to   DATE = '{to}' 
        SET ANSI_NULLS OFF 
        SET ANSI_WARNINGS OFF 
        SET NOCOUNT ON 
        SET ARITHABORT OFF
        EXEC('SELECT * INTO #QUESTS FROM 
        (select 
        CASE WHEN GROUPING(_Q1_PROCODE) = 0 THEN _Q1_PROCODE ELSE ''England'' END AS ''Q1_Org'',
        [_PRIM_REV_PROC_CODE] as Q2_PROC,
        COUNT (_Q1_PROXY_DATE) as ''Q4_Q1Sent'',
        COUNT (_P_REF_HES) as ''Q6_Q1Link'',
        cast(COUNT (_P_REF_HES) *1.0  / Count (_Q1_PROXY_DATE) as decimal (10,7)) as ''Q7_Linkrate'',
        sum (case when _Q2_SENT_FLAG = 1 then 1 else 0 end) as ''Q8_Q2Sent'',
        cast(count (case when _Q2_SENT_FLAG = 1 then 1 end) *1.0 / Count (_Q1_PROXY_DATE) as decimal (10,7)) as ''Q9_Q2IssRate'',
        sum  (case when _Q2_RETURNED_FLAG = 1 then 1 else 0 end) as ''Q10_Q2Returned'',
        cast(sum (case when _Q2_RETURNED_FLAG = 1 then 1 else 0 end) *1.0  / sum (case when _Q2_SENT_FLAG = 1 then 1 else 0 end) as decimal (10,7)) as ''Q11_Q2Resp'' 
        from  proms.QUESTS_{table} 
        where _Q1_PROXY_DATE between \'\'\'+@from+\'\'\' and  \'\'\'+@to+\'\'\' and [_PRIM_REV_PROC_CODE] like ''%-%'' 
        group by [_PRIM_REV_PROC_CODE], rollup(_Q1_PROCODE) 

        union 

        select 
        CASE WHEN GROUPING(_Q1_PROCODE) = 0 THEN _Q1_PROCODE ELSE ''England'' END AS ''Q1_Org'',
        [PROMS_PROC_CODE] as Q2_PROC,
        COUNT (_Q1_PROXY_DATE) as ''Q4_Q1Sent'',
        COUNT (_P_REF_HES) as ''Q6_Q1Link'',
        cast(COUNT (_P_REF_HES) *1.0  / Count (_Q1_PROXY_DATE) as decimal(10,7)) as ''Q7_Linkrate'',
        sum (case when _Q2_SENT_FLAG = 1 then 1 else 0 end) as ''Q8_Q2Sent'',
        cast(count (case when _Q2_SENT_FLAG = 1 then 1 end) *1.0 / Count (_Q1_PROXY_DATE) as decimal (10,7)) as ''Q9_Q2IssRate'',
        sum  (case when _Q2_RETURNED_FLAG = 1 then 1 else 0 end) as ''Q10_Q2Returned'',
        cast(sum (case when _Q2_RETURNED_FLAG = 1 then 1 else 0 end) *1.0  / sum (case when _Q2_SENT_FLAG = 1 then 1 else 0 end) as decimal(10,7)) as ''Q11_Q2Resp'' 
        from  proms.QUESTS_{table} 
        where _Q1_PROXY_DATE between  \'\'\'+@from+\'\'\' and  \'\'\'+@to+\'\'\' 
        and [PROMS_PROC_CODE] in (''hr'',''kr'') 
        group by [PROMS_PROC_CODE], rollup(_Q1_PROCODE))_ 


        SELECT * INTO #HESEPS FROM 
        (select 
        CASE WHEN GROUPING(_P_PROCODE) = 0 THEN _P_PROCODE ELSE ''England'' END AS ''H1_Org'',
        case when PROMS_PROC_CODE =''HR'' and PROC_REVISION_FLAG = 0 then ''HR-PRIM'' 
            when PROMS_PROC_CODE =''HR'' and PROC_REVISION_FLAG = 1 then ''HR-REV'' 
            when PROMS_PROC_CODE =''KR'' and PROC_REVISION_FLAG = 0 then ''KR-PRIM'' 
            when PROMS_PROC_CODE =''KR'' and PROC_REVISION_FLAG = 1 then ''KR-REV'' 
            else PROMS_PROC_CODE 
        end as ''H2_Proc'',
        COUNT (EPIKEY) as ''H3_Episodes'' 
        from proms.HES_PROCEDURES_{table} 
        where EPISTART between  \'\'\'+@from+\'\'\' and  \'\'\'+@to+\'\'\' 
        and PROMS_PROC_CODE in (''hr'',''kr'') 
        group by rollup(_P_PROCODE), PROMS_PROC_CODE,PROC_REVISION_FLAG 

        union 

        select 
        CASE WHEN GROUPING(_P_PROCODE) = 0 THEN _P_PROCODE ELSE ''England'' END AS ''H1_Org'',
        PROMS_PROC_CODE as ''H2_Proc'',
        COUNT (EPIKEY) as ''H3_Episodes'' 
        from proms.HES_PROCEDURES_{table} 
        where EPISTART between  \'\'\'+@from+\'\'\' and  \'\'\'+@to+\'\'\' and PROMS_PROC_CODE in(''hr'',''kr'') 
        group by rollup(_P_PROCODE), PROMS_PROC_CODE 
        )_ 

        SELECT * into #COMBI FROM ( 
        SELECT 
        case when a.H1_Org IS null then b.Q1_Org else a.H1_Org end as QH1_Org,
        case when a.H2_Proc IS null then b.Q2_Proc else a.H2_Proc end as QH2_Proc,
        a.H3_Episodes, b.Q4_Q1Sent, 
        cast (b.Q4_Q1Sent *1.0 / a.H3_Episodes as decimal (10,7)) as QH5_PartRate,
        b.Q6_Q1Link, b.Q7_Linkrate, b.Q8_Q2Sent, b.Q9_Q2IssRate, b.Q10_Q2Returned,
        b.Q11_Q2Resp 
        FROM #HESEPS AS a full outer join #QUESTS AS b 
        ON a.H1_Org = b.Q1_Org and a.H2_Proc = b.Q2_Proc)_ 

        select * into #999 from(select 

        QH1_Org, QH2_Proc,
        case when QH2_Proc<>''AllProc'' and H3_Episodes IN (1,2,3,4,5) then ''-999'' else H3_Episodes END as H3_EPISODES,
        case when QH2_Proc<>''AllProc'' and Q4_Q1Sent IN (1,2,3,4,5) then ''-999'' else Q4_Q1Sent END as Q4_Q1SENT,
        case when QH2_Proc<>''AllProc'' and (H3_Episodes in (1,2,3,4,5) OR Q4_Q1Sent IN (1,2,3,4,5)) then ''-999'' else QH5_PARTRATE end as QH5_PARTRATE,
        case when QH2_Proc<>''AllProc'' and Q4_Q1Sent IN (1,2,3,4,5) and Q6_Q1Link IN (1,2,3,4,5) then ''-999'' else Q6_Q1Link END as Q6_Q1LINK,
        case when QH2_Proc<>''AllProc'' and Q4_Q1Sent IN (1,2,3,4,5) THEN ''-999'' ELSE Q7_Linkrate END AS Q7_LINKRATE,
        case when QH2_Proc<>''AllProc'' and Q4_Q1Sent IN (1,2,3,4,5) and Q8_Q2Sent IN (1,2,3,4,5) then ''-999'' else Q8_Q2Sent END as Q8_Q2SENT,
        case when QH2_Proc<>''AllProc'' and Q4_Q1Sent IN (1,2,3,4,5) THEN ''-999'' ELSE Q9_Q2IssRate END AS Q9_Q2ISSRATE,
        case when QH2_Proc<>''AllProc'' and Q4_Q1Sent IN (1,2,3,4,5) and Q10_Q2Returned IN (1,2,3,4,5) then ''-999'' else Q10_Q2Returned END as Q10_Q2RETURNED,
        case when QH2_Proc<>''AllProc'' and Q4_Q1Sent IN (1,2,3,4,5) THEN ''-999'' ELSE Q11_Q2Resp END AS Q11_Q2RESP 

        from #combi)_ 

        SELECT * into #all from(select 
        QH1_Org,case when grouping(QH2_Proc)=0 then  QH2_Proc else ''AllProc''end as QH2_PROC,
        sum(case when H3_EPISODES<0 then 0 else H3_EPISODES end) as H3_EPISODES,
        sum(case when Q4_Q1SENT<0 then 0 else Q4_Q1SENT end) as Q4_Q1SENT,
        sum(case when QH5_PARTRATE<0 then 0 else QH5_PARTRATE end) as QH5_PARTRATE,
        sum(case when Q6_Q1LINK<0 then 0 else Q6_Q1LINK end) as Q6_Q1LINK,
        sum(case when Q7_LINKRATE<0 then 0 else Q7_LINKRATE end) as Q7_LINKRATE,
        SUM(case when Q8_Q2SENT<0 then 0 else Q8_Q2SENT end) as Q8_Q2SENT,
        sum(case when Q9_Q2ISSRATE<0 then 0 else Q9_Q2ISSRATE end) as Q9_Q2ISSRATE,
        SUM(case when Q10_Q2Returned<0 then 0 else Q10_Q2Returned end) as Q10_Q2Returned,
        sum(case when Q11_Q2RESP<0 then 0 else Q11_Q2RESP end) as Q11_Q2RESP 
        FrOM #999 where QH2_PROC in (''hr'',''kr'') 
        group by QH1_Org,rollup(QH2_Proc) 
        )_ 

        select * into #raw from( 
        SELECT QH1_Org, QH2_PROC, H3_EPISODES, Q4_Q1SENT,
        cast (Q4_Q1Sent *1.0 / H3_Episodes as decimal (10,7)) as QH5_PartRate,
        Q6_Q1LINK,
        cast (Q6_Q1LINK *1.0 / Q4_Q1SENT as decimal (10,7)) as Q7_LinkRate,
        Q8_Q2SENT,
        cast (Q8_Q2SENT *1.0  / Q4_Q1SENT as decimal (10,7)) as Q9_Q2IssRate,
        Q10_Q2Returned,
        cast (Q10_Q2Returned *1.0 / Q8_Q2SENT as decimal (10,7)) as Q11_Q2Resp 
        from #all 
        where QH2_PROC=''AllProc'' 

        union 

        select * FrOM #999)_ 


        SELECT * into #pivot from (select 
        QH1_Org as ''OrgCode'',
        CASE WHEN OrgName is not null THEN OrgName ELSE ''ENGLAND'' END AS ''OrgName'',
        '''
        +'\n\t'.join(procedure_count_all_procedures)+
        '\n\t'.join(procedure_count_HR)+
        '\n\t'.join(procedure_counts_HR_PRIM)+
        '\n\t'.join(procedure_counts_HR_REV)+
        '\n\t'.join(procedure_counts_KR)+
        '\n\t'.join(procedure_counts_KR_PRIM)+
        '\n\t'.join(procedure_counts_KR_REV)[:-2]+
        f'''
        FROM #raw left join proms.REF_ORGS_{table} on QH1_Org=OrgCode 
        group by QH1_Org, OrgName 
        )_ 
        select 
        orgcode as ''Organisation Code'', 
        case when orgname=''England'' then OrgNAme else OrgName +'' (''+OrgCode+'')'' end as ''Organisation Name - SC'','''
        +'\n\t'.join(invalid_data_all_procs)+
        '\n\t'.join(invalid_data_HR)+

        f'''
        
        case when HR_REV_1 in (''-999'',''-999.0000000'') then ''*'' when HR_PRIM_1 in (''-999'',''-999.0000000'') then ''*'' else HR_PRIM_1 end as ''Primary Hip Replacement - Total HES Procedures'', 
        case when HR_REV_2 in (''-999'',''-999.0000000'') then ''*'' when HR_PRIM_2 in (''-999'',''-999.0000000'') then ''*'' else HR_PRIM_2 end as ''Primary Hip Replacement - Total Pre-Op Qs'', 
        case when HR_REV_3 in (''-999'',''-999.0000000'') then ''*'' when HR_PRIM_3 in (''-999'',''-999.0000000'') then ''*'' else HR_PRIM_3 end as ''Primary Hip Replacement - Participation Rate'', 
        case when HR_REV_4 in (''-999'',''-999.0000000'') then ''*'' when HR_PRIM_4 in (''-999'',''-999.0000000'') then ''*'' else HR_PRIM_4 end as ''Primary Hip Replacement - Total Linked'', 
        case when HR_REV_5 in (''-999'',''-999.0000000'') then ''*'' when HR_PRIM_5 in (''-999'',''-999.0000000'') then ''*'' else HR_PRIM_5 end as ''Primary Hip Replacement - Linkage rate'', 
        case when HR_REV_6 in (''-999'',''-999.0000000'') then ''*'' when HR_PRIM_6 in (''-999'',''-999.0000000'') then ''*'' else HR_PRIM_6 end as ''Primary Hip Replacement - Total Q2s sent to date'', 
        case when HR_REV_7 in (''-999'',''-999.0000000'') then ''*'' when HR_PRIM_7 in (''-999'',''-999.0000000'') then ''*'' else HR_PRIM_7 end as ''Primary Hip Replacement - Issue rate'', 
        case when HR_REV_8 in (''-999'',''-999.0000000'') then ''*'' when HR_PRIM_8 in (''-999'',''-999.0000000'') then ''*'' else HR_PRIM_8 end as ''Primary Hip Replacement - Total Q2s returned to date'', 
        case when HR_REV_9 in (''-999'',''-999.0000000'') then ''*'' when HR_PRIM_9 in (''-999'',''-999.0000000'') then ''*'' else HR_PRIM_9 end as ''Primary Hip Replacement - Response rate'', 
        '''+
        '\n\t'.join(invalid_data_HR_REV)+
        '\n\t'.join(invalid_data_KR)
        +f'''
        case when KR_REV_1 in (''-999'',''-999.0000000'') then ''*'' when KR_PRIM_1 in (''-999'',''-999.0000000'') then ''*'' else KR_PRIM_1 end as ''Primary Knee Replacement - Total HES Procedures'', 
        case when KR_REV_2 in (''-999'',''-999.0000000'') then ''*'' when KR_PRIM_2 in (''-999'',''-999.0000000'') then ''*'' else KR_PRIM_2 end as ''Primary Knee Replacement - Total Pre-Op Qs'', 
        case when KR_REV_2 in (''-999'',''-999.0000000'') then ''*'' when KR_PRIM_3 in (''-999'',''-999.0000000'') then ''*'' else KR_PRIM_3 end as ''Primary Knee Replacement - Participation Rate'', 
        case when KR_REV_3 in (''-999'',''-999.0000000'') then ''*'' when KR_PRIM_4 in (''-999'',''-999.0000000'') then ''*'' else KR_PRIM_4 end as ''Primary Knee Replacement - Total Linked'', 
        case when KR_REV_4 in (''-999'',''-999.0000000'') then ''*'' when KR_PRIM_5 in (''-999'',''-999.0000000'') then ''*'' else KR_PRIM_5 end as ''Primary Knee Replacement - Linkage rate'', 
        case when KR_REV_5 in (''-999'',''-999.0000000'') then ''*'' when KR_PRIM_6 in (''-999'',''-999.0000000'') then ''*'' else KR_PRIM_6 end as ''Primary Knee Replacement - Total Q2s sent to date'', 
        case when KR_REV_6 in (''-999'',''-999.0000000'') then ''*'' when KR_PRIM_7 in (''-999'',''-999.0000000'') then ''*'' else KR_PRIM_7 end as ''Primary Knee Replacement - Issue rate'', 
        case when KR_REV_7 in (''-999'',''-999.0000000'') then ''*'' when KR_PRIM_8 in (''-999'',''-999.0000000'') then ''*'' else KR_PRIM_8 end as ''Primary Knee Replacement - Total Q2s returned to date'', 
        case when KR_REV_8 in (''-999'',''-999.0000000'') then ''*'' when KR_PRIM_9 in (''-999'',''-999.0000000'') then ''*'' else KR_PRIM_9 end as ''Primary Knee Replacement - Response rate'', 
        case when KR_REV_1 in (''-999'',''-999.0000000'') then ''*'' else KR_REV_1 end as ''Revision Knee Replacement - Total HES Procedures'', 
        case when KR_REV_2 in (''-999'',''-999.0000000'') then ''*'' else KR_REV_2 end as ''Revision Knee Replacement - Total Pre-Op Qs'', 
        case when KR_REV_3 in (''-999'',''-999.0000000'') then ''*'' else KR_REV_3 end as ''Revision Knee Replacement - Participation Rate'', 
        case when KR_REV_4 in (''-999'',''-999.0000000'') then ''*'' else KR_REV_4 end as ''Revision Knee Replacement - Total Linked'', 
        case when KR_REV_5 in (''-999'',''-999.0000000'') then ''*'' else KR_REV_5 end as ''Revision Knee Replacement - Linkage rate'', 
        case when KR_REV_6 in (''-999'',''-999.0000000'') then ''*'' else KR_REV_6 end as ''Revision Knee Replacement - Total Q2s sent to date'', 
        case when KR_REV_7 in (''-999'',''-999.0000000'') then ''*'' else KR_REV_7 end as ''Revision Knee Replacement - Issue rate'', 
        case when KR_REV_8 in (''-999'',''-999.0000000'') then ''*'' else KR_REV_8 end as ''Revision Knee Replacement - Total Q2s returned to date'', 
        case when KR_REV_9 in (''-999'',''-999.0000000'') then ''*'' else KR_REV_9 end as ''Revision Knee Replacement - Response rate'' 
        from #pivot order by CASE WHEN [Orgcode] = ''England'' THEN 1 ELSE 2 END ASC') 
        DROP TABLE #QUESTS
        DROP TABLE #HESEPS 
        DROP TABLE #COMBI
        DROP TABLE #RAW
        DROP TABLE #999
        drop table #all
        drop table #pivot''')
    return partlinkStr

def provcomm(fromDate,to,fyear,table):
    '''creates the string for the sql provider commision query, inserting the variables into it'''
    provcommStr = (
            f'''DECLARE @from VARCHAR(10) ='{fromDate}'  
            DECLARE @to   VARCHAR(10) ='{to}' 
            DECLARE @fyear VARCHAR(4) = '{fyear}' 
            SET ANSI_NULLS ON 
            SET ANSI_WARNINGS ON 
            SET NOCOUNT ON 
            EXEC(' 
            SELECT * INTO #HES_EPS FROM 
            ( 
            select  
            CASE WHEN GROUPING(_P_PROCODE) = 0 THEN _P_PROCODE ELSE ''England'' END AS ''H1_Org'', 
            case when PROMS_PROC_CODE =''HR'' and PROC_REVISION_FLAG = 0 then ''HR-PRIM'' 
                when PROMS_PROC_CODE =''HR'' and PROC_REVISION_FLAG = 1 then ''HR-REV'' 
                when PROMS_PROC_CODE =''KR'' and PROC_REVISION_FLAG = 0 then ''KR-PRIM'' 
                when PROMS_PROC_CODE =''KR'' and PROC_REVISION_FLAG = 1 then ''KR-REV'' 
                else PROMS_PROC_CODE 
            end as ''H2_Proc'', 
            COUNT (EPIKEY) as ''H3_Episodes'' 
            from proms.HES_PROCEDURES_{table} 
            where EPISTART between \'\'\'+@from+\'\'\' and \'\'\'+@to+\'\'\' 
            group by rollup(_P_PROCODE), PROMS_PROC_CODE, PROC_REVISION_FLAG 
            
            union 
            
            select  
            CASE WHEN GROUPING(_P_PROCODE) = 0 THEN _P_PROCODE ELSE ''England'' END AS ''H1_Org'', 
            PROMS_PROC_CODE as ''H2_Proc'', 
            COUNT (EPIKEY) as ''H3_Episodes'' 
            from proms.HES_PROCEDURES_{table} 
            where EPISTART between \'\'\'+@from+\'\'\' and \'\'\'+@to+\'\'\' and PROMS_PROC_CODE in (''hr'',''kr'') 
            group by rollup(_P_PROCODE), PROMS_PROC_CODE 
            
            union 
            
            select  
            CASE WHEN GROUPING(CCG_CODE) = 0 THEN CCG_CODE ELSE ''England_CCG'' END AS ''H1_Org'', 
            PROMS_PROC_CODE as ''H2_Proc'', 
            COUNT (EPIKEY) as ''H3_Episodes'' 
            from proms.HES_PROCEDURES_{table} 
            where EPISTART between \'\'\'+@from+\'\'\' and \'\'\'+@to+\'\'\' and PROMS_PROC_CODE in (''hr'',''kr'') 
            group by rollup(CCG_CODE), PROMS_PROC_CODE 
            
            union 
            
            select  
            CASE WHEN GROUPING(CCG_CODE) = 0 THEN CCG_CODE ELSE ''England_CCG'' END AS ''H1_Org'', 
            case when PROMS_PROC_CODE =''HR'' and PROC_REVISION_FLAG = 0 then ''HR-PRIM'' 
                when PROMS_PROC_CODE =''HR'' and PROC_REVISION_FLAG = 1 then ''HR-REV'' 
                when PROMS_PROC_CODE =''KR'' and PROC_REVISION_FLAG = 0 then ''KR-PRIM'' 
                when PROMS_PROC_CODE =''KR'' and PROC_REVISION_FLAG = 1 then ''KR-REV'' 
                else PROMS_PROC_CODE 
                end as ''H2_Proc'', 
            COUNT (EPIKEY) as ''H3_Episodes'' 
            from proms.HES_PROCEDURES_{table} 
            where EPISTART between \'\'\'+@from+\'\'\' and \'\'\'+@to+\'\'\' 
            group by rollup(CCG_CODE), PROMS_PROC_CODE, PROC_REVISION_FLAG 
            )_ 
            
            select * into #Union from ( 
            select * 
            from proms.PROMS_AGGREGATED_STATS_{table} a  
            join #hes_eps b on a.orgcode = b.H1_Org and a.ProcGroup = b.H2_Proc 
            where FYear=\'\'\'+@fyear+\'\'\')_ 
            
            select * into #supp1 from(select 
            CONVERT(nvarchar(50),a.OrgCode)+ CONVERT(nvarchar(50),ProcGroup)+ CONVERT(nvarchar(50),Measure) as [Lookup] 
            ,FYear, ProcGroup, Measure, [Version], AggMethod, OrgType, 
            case when a.OrgType=''England'' then ''England'' else b.OrgName end as ''OrgName'', a.OrgCode, 
            case when a.OrgType=''England'' then ''England'' else CONVERT(nvarchar(50),OrgName)+'' (''+ CONVERT(nvarchar(50),a.OrgCode)+'')'' end as OrgNameSC, H3_Episodes as ''Episodes'', 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' else InputCount end as InputCount, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' else AvgQ1 end as Avg01, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' else AvgQ2 end as Avg02, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' else Change end as Change, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' else Improved end as Improved, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' else Same end as Same, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' else Worse end as Worse, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else AdjQ2 end as Adj02, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else AdjHG end as AdjHG, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else StdDev end as StdDev, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else Q2Predicted end as Q2Predicted, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else LCL95 end as LCL95, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else UCL95 end as UCL95, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else LCL998 end as LCL998, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else UCL998 end as UCL998, 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else [Outlier 95%] end as [Outlier 95%], 
            case when H3_Episodes in (1,2,3,4,5) then ''-99'' when InputCount between 1 and 29 then ''-99'' else [Outlier 99.8%] end as [Outlier 99.8%] 
            
            from #Union a 
            left join proms.REF_ORGS_{table} b on a.OrgCode=b.OrgCode)_ 
            
            select * INTO #SUPP2 FROM(SELECT 
            
            Lookup,FYear,ProcGroup,Measure,Version,AggMethod,OrgType,OrgName,OrgCode,Episodes, 
            convert(varchar, InputCount) as InputCount, 
            convert(varchar, Avg01) as Avg01, 
            convert(varchar, Avg02) as Avg02, 
            convert(varchar, Change) as Change, 
            convert(varchar, Improved) as Improved, 
            convert(varchar, Same) as Same, 
            convert(varchar, Worse) as Worse, 
            convert(varchar, Adj02) as Adj02, 
            convert(varchar, AdjHG) as AdjHG, 
            convert(varchar, StdDev) as StdDev, 
            convert(varchar, Q2Predicted) as Q2Predicted, 
            convert(varchar, LCL95) as LCL95, 
            convert(varchar, UCL95) as UCL95, 
            convert(varchar, LCL998) as LCL998, 
            convert(varchar, UCL998) as UCL998, 
            convert(varchar, [Outlier 95%]) as [Outlier 95%], 
            convert(varchar, [Outlier 99.8%]) as [Outlier 99.8%] 
            
            from #supp1)_ 
            
            SELECT * into #supp3 from (select 
            
            case when ProcGroup = ''gh'' then ''Groin Hernia''  
            when ProcGroup = ''vv'' then ''Varicose Vein'' 
            when ProcGroup = ''hr-prim'' then ''Hip Replacement Primary'' 
            when ProcGroup = ''hr-rev'' then ''Hip Replacement Revision'' 
            when ProcGroup = ''hr'' then ''Total Hip Replacement'' 
            when ProcGroup = ''kr-prim'' then ''Knee Replacement Primary'' 
            when ProcGroup = ''kr-rev'' then ''Knee Replacement Revision'' 
            when ProcGroup = ''kr'' then ''Total Knee Replacement'' 
            else null end as ''Procedure'' 
            ,OrgType as ''Organisation Type'',OrgCode  as ''Organisation Code'',OrgName as ''Organsation Name'', 
            case when Measure = ''vas'' then ''EQ VAS'' 
            when Measure = ''index'' then ''EQ-5D Index'' 
            when Measure = ''avvq'' then ''Aberdeen Varicose Vein Questionnaire'' 
            when Measure = ''oks'' then ''Oxford Knee Score'' 
            when Measure = ''ohs'' then ''Oxford Hip Score'' 
            else null end as ''Measure'', 
            CASE WHEN InputCount IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE InputCount end as ''Modelled Records'', 
            Case When Avg01 IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Avg01 end as ''Average Pre-Op Q Score'', 
            Case When Avg02 IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Avg02 end as ''Average Post-Op Q Score'', 
            Case When Change IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Change end as ''Health Gain'', 
            Case When Improved IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Improved end as Improved, 
            Case When Same IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Same end as Same, 
            Case When Worse IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Worse end as Worse, 
            Case When Adj02 IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Adj02 end as ''Adjusted Post-Op Q Score'', 
            Case When AdjHG IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE AdjHG end as ''Adjusted Average Health Gain'', 
            Case When StdDev IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE StdDev end as ''Standard Deviation'' 
            
            FROM #SUPP2 where procgroup not in (''gh'',''vv''))_ 
            
            SELECT * into #supp3sc from (select  
            case when ProcGroup = ''gh'' then ''Groin Hernia''  
            when ProcGroup = ''vv'' then ''Varicose Vein'' 
            when ProcGroup = ''hr-prim'' then ''Hip Replacement Primary'' 
            when ProcGroup = ''hr-rev'' then ''Hip Replacement Revision'' 
            when ProcGroup = ''hr'' then ''Total Hip Replacement'' 
            when ProcGroup = ''kr-prim'' then ''Knee Replacement Primary'' 
            when ProcGroup = ''kr-rev'' then ''Knee Replacement Revision'' 
            when ProcGroup = ''kr'' then ''Total Knee Replacement'' 
            else null end as ''Procedure'' 
            ,OrgType as ''Organisation Type'',OrgCode  as ''Organisation Code'', 
            case when orgtype = ''England'' then ''England''  else OrgName+'' (''+orgcode+'')'' end  as ''Organisation Name'', 
            case when Measure = ''vas'' then ''EQ VAS'' 
            when Measure = ''index'' then ''EQ-5D Index'' 
            when Measure = ''avvq'' then ''Aberdeen Varicose Vein Questionnaire'' 
            when Measure = ''oks'' then ''Oxford Knee Score'' 
            when Measure = ''ohs'' then ''Oxford Hip Score'' 
            else null end as ''Measure'', 
            CASE WHEN InputCount IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE InputCount end as ''Modelled Records'', 
            Case When Avg01 IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Avg01 end as ''Average Pre-Op Q Score'', 
            Case When Avg02 IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Avg02 end as ''Average Post-Op Q Score'', 
            Case When Change IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Change end as ''Health Gain'', 
            Case When Improved IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Improved end as Improved, 
            Case When Same IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Same end as Same, 
            Case When Worse IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Worse end as Worse, 
            Case When Adj02 IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE Adj02 end as ''Adjusted Post-Op Q Score'', 
            Case When AdjHG IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE AdjHG end as ''Adjusted Average Health Gain'', 
            Case When StdDev IN (''-99'') THEN ''*'' when InputCount =''0'' then ''-'' ELSE StdDev end as ''Standard Deviation'' 
            
            FROM #SUPP2 where procgroup not in (''gh'',''vv''))_ 
            select * into #csv1 from (select * from #supp3 where [procedure] =''Total Hip Replacement'')_ 
            select * into #csv2 from (select * from #supp3 where [procedure] =''Hip Replacement Primary'')_ 
            select * into #csv3 from (select * from #supp3 where [procedure] =''Hip Replacement Revision'')_ 
            select * into #csv4 from (select * from #supp3 where [procedure] =''Total Knee Replacement'')_ 
            select * into #csv5 from (select * from #supp3 where [procedure] =''Knee Replacement Primary'')_ 
            select * into #csv6 from (select * from #supp3 where [procedure] =''Knee Replacement Revision'')_ 
            
            select * into #sc1 from (select * from #supp3sc where [procedure] =''Total Hip Replacement'')_ 
            select * into #sc2 from (select * from #supp3sc where [procedure] =''Hip Replacement Primary'')_ 
            select * into #sc3 from (select * from #supp3sc where [procedure] =''Hip Replacement Revision'')_ 
            select * into #sc4 from (select * from #supp3sc where [procedure] =''Total Knee Replacement'')_ 
            select * into #sc5 from (select * from #supp3sc where [procedure] =''Knee Replacement Primary'')_ 
            select * into #sc6 from (select * from #supp3sc where [procedure] =''Knee Replacement Revision'')_ 
            select a.[Procedure],a.[Organisation Type],a.[Organisation Code],a.[Organisation Name],a.[Measure], 
            case when c.[Modelled Records] = ''*'' then b.[Modelled Records] else a.[Modelled Records] end as [Modelled Records], 
            a.[Average Pre-Op Q Score],a.[Average Post-Op Q Score],a.[Health Gain], 
            case when c.[Modelled Records] = ''*'' then b.[Improved] else a.[Improved] end as [Improved], 
            case when c.[Modelled Records] = ''*'' then b.[Same] else a.[Same] end as [Same], 
            case when c.[Modelled Records] = ''*'' then b.[Worse] else a.[Worse] end as [Worse], 
            a.[Adjusted Post-Op Q Score],a.[Adjusted Average Health Gain],a.[Standard Deviation] 
            from #sc1 a 
            left join #sc2 b on a.[Organisation Code]=b.[Organisation Code] and a.measure=b.measure 
            left join #sc3 c on a.[Organisation Code]=c.[Organisation Code] and a.measure=c.measure 
            
            union 
            
            select * from #sc2 
            
            union 
            
            select * from #sc3 
            
            union 
            
            select d.[Procedure],d.[Organisation Type],d.[Organisation Code],d.[Organisation Name],d.[Measure], 
            case when f.[Modelled Records] = ''*'' then e.[Modelled Records] else d.[Modelled Records] end as [Modelled Records], 
            d.[Average Pre-Op Q Score],d.[Average Post-Op Q Score],d.[Health Gain], 
            case when f.[Modelled Records] = ''*'' then e.[Improved] else d.[Improved] end as [Improved], 
            case when f.[Modelled Records] = ''*'' then e.[Same] else d.[Same] end as [Same], 
            case when f.[Modelled Records] = ''*'' then e.[Worse] else d.[Worse] end as [Worse], 
            d.[Adjusted Post-Op Q Score],d.[Adjusted Average Health Gain],d.[Standard Deviation] 
            from #sc4 d 
            left join #sc5 e on d.[Organisation Code]=e.[Organisation Code] and d.measure=e.measure 
            left join #sc6 f on d.[Organisation Code]=f.[Organisation Code] and d.measure=f.measure 
            union select * from #sc5 
            union select * from #sc6 
            order by [Procedure],[Organisation Type],[Measure],[Organisation Name]') '''
            )
    return provcommStr


def funneldata(table,fyear,aggmethod):
    '''creates the string for the sql funnel data query, inserting the variables into it'''

    funneldataStr = f'''EXEC('SELECT case when S.ProcGroup IN (''KR'',''HR'') then ''Total ''+ RP.Description else RP.Description end AS ''Procedure'', 
        RM.[Description] AS Measure, S.InputCount AS ''Modelled Records'', 
        S.AvgQ2 AS ''Average Post-Op Q Score'', S.AdjHG AS ''Adjusted Average Health Gain'', 
        S.UCL998 AS ''Upper Control Limit 99.8'', S.StdDev AS ''Standard Deviation'' 
        FROM proms.PROMS_AGGREGATED_STATS_{table} S 
        
        LEFT JOIN proms.REF_PROCEDURES RP ON S.ProcGroup = RP.PROMs_PROC_CODE 
        LEFT JOIN proms.REF_MEASURES RM ON S.Measure = RM.Measure 
        
        WHERE FYear = {fyear} 
        AND AggMethod = ''{aggmethod} '' 
        AND ((Version = ''Model2'' AND S.ProcGroup IN (''KR'', ''HR'')) 
        OR (Version = ''Model3'' AND S.ProcGroup IN (''KR-PRIM'', ''KR-REV'', ''HR-PRIM'', ''HR-REV''))) 
        AND S.ORGCODE = ''England'' 
    
        ORDER BY [Procedure], 
        CASE WHEN S.Measure = ''INDEX'' THEN 1 
        WHEN S.Measure = ''VAS'' THEN 2 
        ELSE 3 
        END ')'''
    return funneldataStr