import datetime
import numpy as np
import pandas as pd
import warnings

import pdb

warnings.simplefilter(action='ignore', category=UserWarning)

#get behavior data with associated intensity and duration values. 
def get_month_with_dur_int(workbook_xl, month):
    #set dataframe display options 
    pd.options.display.max_columns = 200
    pd.options.display.max_rows = 200

    #read in necessary sheets 
    df = pd.read_excel(workbook_xl, sheet_name=month, skiprows=[1,2])
    print('workbook\n:',df)
    dfinfo = pd.read_excel(workbook_xl, sheet_name=0)
    dfstudet = pd.read_excel(workbook_xl, sheet_name=2, header=None)
    
    #get years variable 
    year = dfinfo.iloc[3,1]
    year1, year2 = str.split(year, '-')
    
    #get name
    # name = dfstudet.iloc[0,0]
    # print(f"name is {name}")
    
    # pdb.set_trace()
    #select necessary columns and front fill NaNs in month column 
    dfbeh = df.iloc[:, [0,1,2,4,7,22,25,40,43,58,61,76,79]]

    # print(dfbeh.head())
    dfbeh = dfbeh.rename(columns = {'Unnamed: 1':'Shift','Unnamed: 2':'No Data','Unnamed: 7':str(dfbeh.columns[3])+'_beh','Unnamed: 25':str(dfbeh.columns[5])+'_beh',
                                    'Unnamed: 43':str(dfbeh.columns[7])+'_beh','Unnamed: 61':str(dfbeh.columns[9])+'_beh','Unnamed: 79':str(dfbeh.columns[11])+'_beh'})
    
    #print(dfbeh.iloc[:,0])
    dfbeh.iloc[:,0] = dfbeh.iloc[:,0].fillna(method='ffill')
    #print(dfbeh.iloc[:,0])

    #create 'month number' variable 
    month_name = dfbeh.columns[0]
    datetime_object = datetime.datetime.strptime(month_name, "%B")
    month_num = datetime_object.month

    #if month number is between 7 and 12 year1 is selected, else year2 
    if 7 <= month_num <= 12:
        year_num = year1
    else:
        year_num = year2

    #create date string 
    date = str(year_num) + '-' + str(month_num)

    #create list of colum indexes for behavior data 
    beh_indexes = [4,6,8,10,12]

    #loop through behavior indexes and create dataframes for each behavior 
    behdfs = []
    for i, bidx in enumerate(beh_indexes):
        #create new var for each df 
        beh_id = f"beh{i+1}" 
        #create long format df for behavior and drop unnecessary rows 
        beh_id = pd.melt(dfbeh, id_vars = [dfbeh.columns[0],dfbeh.columns[1],dfbeh.columns[2]],value_vars =[dfbeh.columns[bidx]])
        beh_id = beh_id.drop(beh_id.index[np.where(beh_id.index >= 93)])

        if month_num == 4 or month_num == 6 or month_num == 9 or month_num == 11:
            beh_id = beh_id.drop(beh_id.index[np.where(beh_id.index >= 90)])
        elif month_num ==2:
            beh_id = beh_id.drop(beh_id.index[np.where(beh_id.index >= 84)])
        else:
            beh_id = beh_id
        #add dfs to list 
        behdfs.append(beh_id)

    #cocatanate into one lare dataframe, drop unnecessary rows 
    behs = pd.concat(behdfs)
    
    behs = behs[~behs['variable'].isin(['Insert_beh'])]
    #tidy up variable names and reset index
    behs['variable'] = behs['variable'].str.replace(r'_beh', '')
    behs.reset_index(drop = True,inplace=True)
    #create date column and convery to padas datetime
    behs['Date'] = date + '-' + behs.iloc[:,0].astype(str)
    behs['Date'] = pd.to_datetime(behs['Date'])
    
    #clean up values, return NaN for all unrecognized strings (ie ".")
    values = behs['value']
    for value_i, val in enumerate(values):
        try: 
            behs['value'][value_i] = float(behs['value'][value_i])
        except:
            behs['value'][value_i] = float("NaN")

    #get the name of the first column, which we drop
    month_to_remove = behs.columns[0]
    return behs.drop(month_to_remove, axis=1)

#define a function encapsulting above code so that we can get data for one month
def get_month_dataframe(workbook_xl, month):
    #set dataframe display options 
    pd.options.display.max_columns = 200
    pd.options.display.max_rows = 200

    #read in necessary sheets 
    df = pd.read_excel(workbook_xl, sheet_name=month, skiprows=[1,2])
    dfinfo = pd.read_excel(workbook_xl, sheet_name=0)
    dfstudet = pd.read_excel(workbook_xl, sheet_name=2, header=None)
    
    #get years variable 
    year = dfinfo.iloc[3,1]
    year1, year2 = str.split(year, '-')
    
    #get name
    # name = dfstudet.iloc[0,0]
    # print(f"name is {name}")
    
    # pdb.set_trace()
    #select necessary columns and front fill NaNs in month column 
    dfbeh = df.iloc[:, [0,1,2,4,7,22,25,40,43,58,61,76,79]]
    #print(dfbeh.head())
    dfbeh = dfbeh.rename(columns = {'Unnamed: 1':'Shift','Unnamed: 2':'No Data','Unnamed: 7':str(dfbeh.columns[3])+'_beh','Unnamed: 25':str(dfbeh.columns[5])+'_beh',
                                    'Unnamed: 43':str(dfbeh.columns[7])+'_beh','Unnamed: 61':str(dfbeh.columns[9])+'_beh','Unnamed: 79':str(dfbeh.columns[11])+'_beh'})
    
    #print(dfbeh.iloc[:,0])
    dfbeh.iloc[:,0] = dfbeh.iloc[:,0].fillna(method='ffill')
    #print(dfbeh.iloc[:,0])

    

    #create 'month number' variable 
    month_name = dfbeh.columns[0]
    datetime_object = datetime.datetime.strptime(month_name, "%B")
    month_num = datetime_object.month

    #if month number is between 7 and 12 year1 is selected, else year2 
    if 7 <= month_num <= 12:
        year_num = year1
    else:
        year_num = year2

    #create date string 
    date = str(year_num) + '-' + str(month_num)

    #create list of colum indexes for behavior data 
    beh_indexes = [4,6,8,10,12]

    #loop through behavior indexes and create dataframes for each behavior 
    behdfs = []
    for i, bidx in enumerate(beh_indexes):
        #create new var for each df 
        beh_id = f"beh{i+1}" 
        #create long format df for behavior and drop unnecessary rows 
        beh_id = pd.melt(dfbeh, id_vars = [dfbeh.columns[0],dfbeh.columns[1],dfbeh.columns[2]],value_vars =[dfbeh.columns[bidx]])
        beh_id = beh_id.drop(beh_id.index[np.where(beh_id.index >= 93)])

        
        if month_num == 4 or month_num == 6 or month_num == 9 or month_num == 11:
            beh_id = beh_id.drop(beh_id.index[np.where(beh_id.index >= 90)])
        elif month_num ==2:
            beh_id = beh_id.drop(beh_id.index[np.where(beh_id.index >= 84)])
        else:
            beh_id = beh_id
        #add dfs to list 
        behdfs.append(beh_id)

    #cocatanate into one lare dataframe, drop unnecessary rows 
    behs = pd.concat(behdfs)
    
    behs = behs[~behs['variable'].isin(['Insert_beh'])]
    #tidy up variable names and reset index
    behs['variable'] = behs['variable'].str.replace(r'_beh', '')
    behs.reset_index(drop = True,inplace=True)
    #create date column and convery to padas datetime
    behs['Date'] = date + '-' + behs.iloc[:,0].astype(str)
    behs['Date'] = pd.to_datetime(behs['Date'])
    
    

    #clean up values, return NaN for all unrecognized strings (ie ".")
    values = behs['value']
    for value_i, val in enumerate(values):
        try: 
            behs['value'][value_i] = float(behs['value'][value_i])
        except:
            behs['value'][value_i] = float("NaN")

    #get the name of the first column, which we drop
    month_to_remove = behs.columns[0]
    return behs.drop(month_to_remove, axis=1)

#aggregates all months data into a single data frame
def get_all_months_df(workbook_xl):
    months = ['July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'June']
    xl_file = pd.ExcelFile(workbook_xl)                
    months_data = []
    
    for month in months:
        df_month = get_month_dataframe(xl_file, month)
        months_data.append(df_month)
    return pd.concat(months_data)

#aggregates all months data into a single data frame with associated intensity and duration values.
def get_all_months_int_dur(workbook_xl):
    months = ['July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'June']
    xl_file = pd.ExcelFile(workbook_xl)                
    months_data = []
    
    for month in months:
        df_month = get_month_with_dur_int(xl_file, month)
        months_data.append(df_month)
    return pd.concat(months_data)

# gets data for medication that begins on column = start_column_index
# medications are seperated by 9 columns in the workbook, so medication 1
# starts on column 0, medication 2 starts on column 9, etc. 
def get_med_data(workbook_xl, start_column_index=0):
    df_meds = pd.read_excel(workbook_xl, sheet_name="MEDICATIONS", skiprows=[0, 1])
    df_meds_id = pd.read_excel(workbook_xl, sheet_name="MEDICATIONS", skiprows=[0, 3])
    med_name = df_meds_id.columns[start_column_index]
    df_meds = df_meds.drop(index=0)
    dose = pd.DataFrame(df_meds.iloc[:,start_column_index])
    units = pd.DataFrame(df_meds.iloc[:,start_column_index + 1])
    dose_frames =  [dose, units]
    df_dose = pd.concat(dose_frames, axis=1)
    df_dose["Medication"] = med_name
    # drop NaNs
    df_dose = df_dose.dropna()
    #rename columns to avoid things like "Dose.1"
    df_dose = df_dose.rename(columns={df_dose.columns[0] : "Dose", df_dose.columns[1] : "Units"})
    
    # get and format start date
    start_month_df = pd.DataFrame(df_meds.iloc[:,start_column_index + 2])
    # deal with column names like START DATE.1
    med_num = int(start_column_index / 9)
    med_num_str = ""
    if med_num > 0:
        med_num_str = "." + str(med_num)

    start_month_df = start_month_df.rename(columns={"START DATE"+med_num_str : "Month"})
    start_day_df = pd.DataFrame(df_meds.iloc[:,start_column_index + 3])
    start_day_df = start_day_df.rename(columns={"Unnamed: " + str(start_column_index + 3) : "Day"})
    start_year_df = pd.DataFrame(df_meds.iloc[:,start_column_index + 4])
    start_year_df = start_year_df.rename(columns={"Unnamed: " + str(start_column_index + 4) : "Year"})
    start_date_frames = [start_month_df, start_day_df, start_year_df]
    df_start_date = pd.concat(start_date_frames, axis=1)
    df_start_date = df_start_date.dropna()
    df_start_date = pd.to_datetime(df_start_date)

    # get and format end date
    end_month_df = pd.DataFrame(df_meds.iloc[:,start_column_index + 5])
    end_month_df = end_month_df.rename(columns={"END DATE"+med_num_str : "Month"})
    end_day_df = pd.DataFrame(df_meds.iloc[:,start_column_index + 6])
    end_day_df = end_day_df.rename(columns={"Unnamed: " + str(start_column_index + 6) : "Day"})
    end_year_df = pd.DataFrame(df_meds.iloc[:,start_column_index + 7])
    end_year_df = end_year_df.rename(columns={"Unnamed: " + str(start_column_index + 7) : "Year"})
    end_date_frames = [end_month_df, end_day_df, end_year_df]
    df_end_date = pd.concat(end_date_frames, axis=1)
    df_end_date = df_end_date.dropna()
    df_end_date = pd.to_datetime(df_end_date)

    # combine "start date" and "end date" into a single data frame
    df_dates = pd.DataFrame()
    df_dates["Start Date"] = df_start_date
    df_dates["End Date"] = df_end_date

    combined_frames = [df_dose, df_dates]
    combined_df = pd.concat(combined_frames, axis=1)
    return combined_df

# get all medication data by appending calls to the above get_med_data function
def get_all_meds_data(workbook_xl):
    start_column_index = 0
    med_dfs = []
    num_columns = len(pd.read_excel(workbook_xl, sheet_name="MEDICATIONS").columns)
    while start_column_index < num_columns:
        med_dfs.append(get_med_data(workbook_xl, start_column_index))
        start_column_index += 9 # each medication is seperated by 9 columns
    return pd.concat(med_dfs)