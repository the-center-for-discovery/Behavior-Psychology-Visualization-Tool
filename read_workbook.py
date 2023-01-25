import datetime
import numpy as np
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=UserWarning)

#define a function encapsulting above code so that we can get data for one month
def get_month_dataframe(workbook_xl, month):
    #set dataframe display options 
    pd.options.display.max_columns = 200
    pd.options.display.max_rows = 200

    #read in necessary sheets 
    df = pd.read_excel(workbook_xl, sheet_name=month, skiprows=[1,2])
    dfyr = pd.read_excel(workbook_xl, sheet_name=0)
    print(dfyr)

    #get years variable 
    year = dfyr.iloc[3,1]
    print(year)
    year1, year2 = str.split(year, '-')
    

    #select necessary columns and front fill NaNs in month column 
    dfbeh = df.iloc[:, [0,1,2,4,7,22,25,40,43,58,61,76,79]]
    dfbeh = dfbeh.rename(columns = {'Unnamed: 1':'Shift','Unnamed: 2':'No Data','Unnamed: 7':dfbeh.columns[3]+'_beh','Unnamed: 25':dfbeh.columns[5]+'_beh',
                                    'Unnamed: 43':dfbeh.columns[7]+'_beh','Unnamed: 61':dfbeh.columns[9]+'_beh','Unnamed: 79':dfbeh.columns[11]+'_beh'})
    dfbeh.iloc[:,0] = dfbeh.iloc[:,0].fillna(method='ffill')

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
