from __future__ import print_function
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import calendar
import seaborn as sns
import sqlite3 as sq3
import time
import datetime
import scipy as sc
import os
import mysql.connector
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual
from IPython.display import Javascript, display, Markdown
import ipywidgets as widgets
import warnings

os.system("jupyter nbextension enable --py widgetsnbextension")     # Guarantes that the widgets will show on any os in Python 3
warnings.filterwarnings('ignore')                                   # Gets rid of warning messages in the notebook

#####################################################
##### Section 1 : Data Import Related Functions #####
#####################################################

def readDataSmaller(plantName, unitName):
    """
    This function imports the data from 'smaller.db' when the program needs to be run locally
    Very usefull for devolopment or when AWS is down.
    Currently not selectable in the UI, most likely will not be useful again in the future.
    Kept here, as well as associated functions, in case it is needed for development again.
    Much slower than AWS because it used sqlite.
    """

    con = sq3.connect('smaller.db')

    data = pd.read_sql("select * FROM data WHERE name = '"+plantName+"' AND unitid = '"+unitName+"'", con)

    data['GLOAD']=data['gload']
    # Replace lines should not be necessary anymore, not tested for local case though.
    data['GLOAD'].replace('', 0, inplace=True)
    data['CO2_MASS'].replace('', 0, inplace=True)
    data['SO2_MASS'].replace('', 0, inplace=True)
    data['NOX_MASS'].replace('', 0, inplace=True)
    data['heat_input'].replace('', 0, inplace=True)
    data['HEAT_INPUT']=data['heat_input']
    data['op_time'].replace('', np.nan, inplace=True)
    data['OP_TIME']=data['op_time']

    max_gen_ht=data['heat_input'].astype(float).max()
    max_gen_gl=data['GLOAD'].astype(float).max()
    data['CO2eI_ht']=(907.18474*data['CO2_MASS'].astype(float)+298*0.45359237*data['NOX_MASS'].astype(float))/data['heat_input'].astype(float)
    data['CO2eI_gl']=(907.18474*data['CO2_MASS'].astype(float)+298*0.45359237*data['NOX_MASS'].astype(float))/(data['GLOAD'].astype(float)*data['op_time'].astype(float))
    data['CO2I_ht']=907.18474*data['CO2_MASS'].astype(float)/data['heat_input'].astype(float)
    data['CO2I_gl']=907.18474*data['CO2_MASS'].astype(float)/(data['GLOAD'].astype(float)*data['op_time'].astype(float))
    data['SO2I_ht']=0.45359237*data['SO2_MASS'].astype(float)/data['heat_input'].astype(float)
    data['SO2I_gl']=0.45359237*data['SO2_MASS'].astype(float)/(data['GLOAD'].astype(float)*data['op_time'].astype(float))
    data['NOXI_ht']=0.45359237*data['NOX_MASS'].astype(float)/data['heat_input'].astype(float)
    data['NOXI_gl']=0.45359237*data['NOX_MASS'].astype(float)/(data['GLOAD'].astype(float)*data['op_time'].astype(float))
    data['capacityFactor_ht']=data['heat_input'].astype(float)/max_gen_ht
    data['capacityFactor_gl']=data['GLOAD'].astype(float)*data['op_time'].astype(float)/max_gen_gl

    data['CO2I_gl'].replace('', 0, inplace=True)
    data['CO2I_ht'].replace('', 0, inplace=True)


    print("Data successfully extracted.")

    return data

def readDataAWS(plantName, unitName):
    """
    This function imports and formats the data from the AWS server.
    """
    
    # Import and turn into Pandas dataframe
    server = mysql.connector.connect(user="widap", password="widap123", 
                              host="widapdb-cluster-1.cluster-cpyvkv2lasim.us-west-1.rds.amazonaws.com",
                              database="widap")

    query = server.cursor(buffered=True)
    query.execute("SELECT STATE,NAME,ORISPL_CODE,UNITID,OP_DATE,OP_HOUR,OP_TIME,GLOAD,op_datetime as DATETIME,SLOAD,SO2_MASS,SO2_RATE,NOX_MASS,NOX_RATE,CO2_MASS,CO2_RATE,HEAT_INPUT FROM wecc WHERE NAME = '{}' AND UNITID = '{}'".format(plantName,unitName))
    data = pd.DataFrame(data=query.fetchall(), index = None, columns = query.column_names)   

    query.close()
    server.close()

    data.columns = data.columns.astype(str)             # Solves issue where columns names where bytes and not str

    # Format data and add additional colums
    max_gen_ht=data['HEAT_INPUT'].astype(float).max()
    max_gen_gl=data['GLOAD'].astype(float).max()
    data['CO2eI_ht']=(907.18474*data['CO2_MASS'].astype(float)+298*0.45359237*data['NOX_MASS'].astype(float))/data['HEAT_INPUT'].astype(float)
    data['CO2eI_gl']=(907.18474*data['CO2_MASS'].astype(float)+298*0.45359237*data['NOX_MASS'].astype(float))/(data['GLOAD'].astype(float)*data['OP_TIME'].astype(float))
    data['CO2I_ht']=907.18474*data['CO2_MASS'].astype(float)/data['HEAT_INPUT'].astype(float)
    data['CO2I_gl']=907.18474*data['CO2_MASS'].astype(float)/(data['GLOAD'].astype(float)*data['OP_TIME'].astype(float))
    data['SO2I_ht']=0.45359237*data['SO2_MASS'].astype(float)/data['HEAT_INPUT'].astype(float)
    data['SO2I_gl']=0.45359237*data['SO2_MASS'].astype(float)/(data['GLOAD'].astype(float)*data['OP_TIME'].astype(float))
    data['NOXI_ht']=0.45359237*data['NOX_MASS'].astype(float)/data['HEAT_INPUT'].astype(float)
    data['NOXI_gl']=0.45359237*data['NOX_MASS'].astype(float)/(data['GLOAD'].astype(float)*data['OP_TIME'].astype(float))
    data['capacityFactor_ht']=data['HEAT_INPUT'].astype(float)/max_gen_ht
    data['capacityFactor_gl']=data['GLOAD'].astype(float)*data['OP_TIME'].astype(float)/max_gen_gl

    data.sort_values(by=['DATETIME'],inplace=True)      # Necessary for time series

    # Return correctly formated data
    print("Data successfully extracted.")  
    return data

def formatData(data):
    """
    Format data function, only usefull when importing from local smaller.db file.
    Mostly obsolete (as long as AWS keeps running properly)
    """

    #For import from smaller only!
    data['MONTH'] = data['op_date'].astype(str).str[:2]# extract month
    data['DAY'] = data['op_date'].astype(str).str[3:5]
    data['Year_Month'] = data['year'].astype(int)*100 + data['MONTH'].astype(int) # change back to 6?
    data['op_fulltime']=data['year'].astype(str)+data['MONTH'].astype(str)+data['DAY'].astype(str)+':'+data['op_hour'].astype(str)
    data['ts_time']=pd.to_datetime(data['op_fulltime'],format='%Y%m%d:%H')
    data.index=pd.to_datetime(data['op_fulltime'],format='%Y%m%d:%H')
    data['sorter']=(data['year'].astype(str)+data['MONTH'].astype(str)+data['DAY'].astype(str)+(data['op_hour'].astype(float)/10).astype(str)).astype(float)
    data.sort_values(by=['sorter'],inplace=True)

    print("data successfully formated")
    return data

##########################################
##### Section 2 : Plotting Functions #####
##########################################

def CF_boxplot(data,plantName,unitName,yearRange):
    """
    Function generating our first visualization.
    Monthly boxplot of generation.
    """

    # Turn year range slider into start and end values
    startYear=yearRange[0]
    endYear=yearRange[1]

    # Create and show plot
    boxprops = dict(linestyle='-', linewidth=1, color='k')
    medianprops = dict(linestyle='-', linewidth=3, color='k')
    plt.figure(2)
    bp = data.boxplot(column='GLOAD',by='Year_Month',showfliers=False,figsize=(24,8),widths = 0.2,boxprops=boxprops, medianprops=medianprops,return_type='dict')
    plt.title("Monthly Boxplot of Gross Generatation - "+ plantName + " " + unitName,Fontsize=28)
    plt.suptitle("")
    plt.xlabel('Year',Fontsize=20)
    plt.xticks([1, 13, 25, 37, 49, 61, 73, 85, 97, 109, 121, 133, 145, 157, 169, 183, 195], ['2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011', '2012', '2013', '2014', '2015', '2016','2017'])
    plt.ylabel("Gross Generation [MWh]",Fontsize=20)
    plt.xlim((startYear-2001)*12+1,(endYear+1-2001)*12+1)
    plt.tick_params(axis='both',labelsize=16)
    plt.show()

def Norm_Em(data,plantName,unitName,yearRange,RM_window,CO2_on,SO2_on,NOX_on):
    """
    Function generating the second visualization
    Rolling mean of emissions
    """

    # Turn year range slider into start and end values
    startYear=yearRange[0]
    endYear=yearRange[1]

    RM_window=24*RM_window      # Convert rolling mean window from days to hours
    leg=[]
    plt.figure(2,figsize=(24,8))
    # For each emission selected, create time series, add it to plot and concatenate legend
    if CO2_on:
        CO=pd.Series.rolling(data['CO2_MASS']/data['CO2_MASS'].mean(), window=RM_window,min_periods=min(3,RM_window)).mean()
        plt.plot(CO[str(startYear):str(endYear)],linewidth=0.7)
        leg.append('CO2')
    if SO2_on:
        SO=pd.Series.rolling(data['SO2_MASS']/data['SO2_MASS'].mean(), window=RM_window,min_periods=min(3,RM_window)).mean()
        plt.plot(SO[str(startYear):str(endYear)],linewidth=0.7)
        leg.append('SO2')
    if NOX_on:
        NO=pd.Series.rolling(data['NOX_MASS']/data['NOX_MASS'].mean(), window=RM_window,min_periods=min(3,RM_window)).mean()
        plt.plot(NO[str(startYear):str(endYear)],linewidth=0.7)
        leg.append('NOX')
    # Format and show plot
    plt.xlabel('Time',Fontsize=20)
    plt.ylabel('Normalized Emissions',Fontsize=20)
    plt.legend(leg,fontsize=20)
    plt.title("Normalized Emissions Time Series - "+ plantName + " " + unitName,Fontsize=28)
    plt.tick_params(axis='both',labelsize=16)
    plt.show()

def EmvCF(data,plantName,unitName,yearRange,Nplots,CO2scale,SO2scale):
    """
    Function generating third visualization
    Emission against capacity factor scatter plot
    """

    # Turn year range slider into start and end values
    startYear=yearRange[0]
    endYear=yearRange[1]

    # Generate list of years to plot
    yearsToPlot = np.linspace(startYear,endYear,Nplots).astype(int)

    # Generate plot for each year on that list
    ii=1
    plt.figure(1,figsize=(24,8))
    for ii in range(Nplots):
        year=yearsToPlot[ii]
        plt.subplot(1,2,1)
        plt.plot(data[data['year']==year]['capacityFactor_gl'],data[data['year']==year]['CO2I_gl'],'.', markersize=3)
        plt.ylim(0,CO2scale*data['CO2I_gl'].median())
        plt.ylabel('CO2 Intensity [kg/MWh]',Fontsize=20)
        plt.xlabel('Capacity Factor',Fontsize=20)
        plt.tick_params(axis='both',labelsize=16)
        plt.subplot(1,2,2)
        plt.plot(data[data['year']==year]['capacityFactor_gl'],data[data['year']==year]['SO2I_gl'],'.', markersize=3)
        plt.ylim(0,SO2scale*data['SO2I_gl'].median())
        plt.ylabel('SO2 Intensity [kg/MWh]',Fontsize=20)
        plt.xlabel('Capacity Factor',Fontsize=20)
        plt.tick_params(axis='both',labelsize=16)
    plt.suptitle("Emissions Intensity against Capacity Factor (CO2 and SO2) - "+ plantName + " " + unitName,fontsize=28)
    plt.legend(yearsToPlot,fontsize=20)
    plt.show()

def emissionHistograms(data,plantName,unitName,yearRange,eff_on,CapFac_on,CO2e_on,CO2_on,SO2_on,NOX_on):
    """
    Function for our fourth visualization
    Histograms to identify operation and emission modes.
    """

    # Turn year range slider into start and end values
    startYear=yearRange[0]
    endYear=yearRange[1] 

    # Create additional variables   
    heatRate = (data['HEAT_INPUT'] * 1e6) / (data['OP_TIME'] * data['GLOAD'] * 1e3)
    efficiency = (data['OP_TIME'] * data['GLOAD']) / (data['HEAT_INPUT'] * 0.29307107)
    
    # For each metric selected, generate the histogram
    if eff_on:
        plt.figure(6,figsize=(24,6))
        plt.hist(efficiency[str(startYear):str(endYear)],100,[0,1.0])
        plt.xlabel('Efficiency',Fontsize=20)
        plt.ylabel('Counts',Fontsize=20)
        plt.title("Histogram of Observed Efficiency Values - "+ plantName + " " + unitName + " - " + str(startYear) + " to " +str(endYear),Fontsize=28)
        plt.tick_params(axis='both',labelsize=16)
        plt.show() 

    if CapFac_on:
        plt.figure(6,figsize=(24,6))
        plt.suptitle("Capacity Factor Histogram - "+ plantName + " " + unitName + " - " + str(startYear) + " to " +str(endYear), fontsize=28)
        plt.subplot(121)
        plt.hist((data['capacityFactor_ht'].dropna())[str(startYear):str(endYear)], 100, facecolor='y',log=False)
        plt.ylabel('Counts',Fontsize=20)
        plt.xlabel('Capacity Factor from Heat Input',Fontsize=20)
        plt.tick_params(axis='both',labelsize=16)
        plt.subplot(122)
        plt.hist((data['capacityFactor_gl'].dropna())[str(startYear):str(endYear)], 100, facecolor='y',log=False)
        plt.ylabel('Counts',Fontsize=20)
        plt.xlabel('Capacity Factor from Generation',Fontsize=20)
        plt.subplots_adjust(wspace = 0.5)
        plt.tick_params(axis='both',labelsize=16)
        plt.show()

    if CO2e_on:
        plt.figure(5,figsize=(24,6))
        plt.suptitle("CO2 Equivalent Intensity Histogram - "+ plantName + " " + unitName + " - " + str(startYear) + " to " +str(endYear), fontsize=28)
        plt.subplot(121)
        plt.hist((data['CO2eI_ht'].dropna())[str(startYear):str(endYear)], 100, facecolor='g',log=False)
        plt.ylabel('Counts',Fontsize=20)
        plt.xlabel('CO2e Intensity from Heat Input (kg/MWh)',Fontsize=20)
        plt.tick_params(axis='both',labelsize=16)
        plt.subplot(122)
        plt.hist((data['CO2eI_gl'].dropna())[str(startYear):str(endYear)], 100, range=[0, 3*data['CO2eI_gl'].median()], facecolor='g',log=False)
        plt.ylabel('Counts',Fontsize=20)
        plt.tick_params(axis='both',labelsize=16)
        plt.xlabel('CO2e Intensity from Generation (kg/MWh)',Fontsize=20)
        plt.subplots_adjust(wspace = 0.5)
        plt.show()

    if CO2_on:
        plt.figure(5,figsize=(24,6))
        plt.suptitle("CO2 Intensity Histogram - "+ plantName + " " + unitName + " - " + str(startYear) + " to " +str(endYear), fontsize=28)
        plt.subplot(121)
        plt.hist((data['CO2I_ht'].dropna())[str(startYear):str(endYear)], 100, facecolor='g',log=False)#range=[54, 58],
        plt.ylabel('Counts',Fontsize=20)
        plt.xlabel('CO2 Intensity from Heat Input (kg/MWh)',Fontsize=20)
        plt.tick_params(axis='both',labelsize=16)
        plt.subplot(122)
        plt.hist((data['CO2I_gl'].dropna())[str(startYear):str(endYear)], 100, range=[0, 3*data['CO2I_gl'].median()], facecolor='g',log=False)
        plt.ylabel('Counts',Fontsize=20)
        plt.xlabel('CO2 Intensity from Generation (kg/MWh)',Fontsize=20)
        plt.subplots_adjust(wspace = 0.5)
        plt.tick_params(axis='both',labelsize=16)
        plt.show()

    if SO2_on:
        plt.figure(5,figsize=(24,6))
        plt.suptitle("SO2 Intensity Histogram - "+ plantName + " " + unitName + " - " + str(startYear) + " to " +str(endYear), fontsize=28)
        plt.subplot(121)
        plt.hist((data['SO2I_ht'].dropna())[str(startYear):str(endYear)], 100, facecolor='g',log=False)#range=[54, 58],
        plt.ylabel('Counts',Fontsize=20)
        plt.xlabel('SO2 Intensity from Heat Input (kg/MWh)',Fontsize=20)
        plt.tick_params(axis='both',labelsize=16)
        plt.subplot(122)
        plt.hist((data['SO2I_gl'].dropna())[str(startYear):str(endYear)], 100, range=[0, 3*data['SO2I_gl'].median()], facecolor='g',log=False)
        plt.ylabel('Counts',Fontsize=20)
        plt.xlabel('SO2 Intensity from Generation (kg/MWh)',Fontsize=20)
        plt.subplots_adjust(wspace = 0.5)
        plt.tick_params(axis='both',labelsize=16)
        plt.show()

    if NOX_on:
        plt.figure(5,figsize=(24,6))
        plt.suptitle("NOX Intensity Histogram - "+ plantName + " " + unitName + " - " + str(startYear) + " to " +str(endYear), fontsize=28)
        plt.subplot(121)
        plt.hist((data['NOXI_ht'].dropna())[str(startYear):str(endYear)], 100, facecolor='g',log=False)#range=[54, 58],
        plt.ylabel('Counts',Fontsize=20)
        plt.xlabel('NOX Intensity from Heat Input (kg/MWh)',Fontsize=20)
        plt.tick_params(axis='both',labelsize=16)
        plt.subplot(122)
        plt.hist((data['NOXI_gl'].dropna())[str(startYear):str(endYear)], 100, range=[0, 3*data['NOXI_gl'].median()], facecolor='g',log=False)
        plt.ylabel('Counts',Fontsize=20)
        plt.xlabel('NOX Intensity from Generation (kg/MWh)',Fontsize=20)
        plt.subplots_adjust(wspace = 0.5)
        plt.tick_params(axis='both',labelsize=16)
        plt.show()

#########################################################
##### Section 3 : Jupyter Display Related Functions #####
#########################################################

def printmd(string):
    """
    Just a simple function to display stuff in Jupyter Notebook markdown mode.
    """
    display(Markdown(string))

def interactive_plots(data,plantName,unitName):
    """
    Generate all the interactive plots
    """

    # Make all the widgets
    year_select=widgets.IntRangeSlider(value=[2001, 2017],min=2001,  max=2017, step=1, description='Range:')        # Year Range, common across plots
    RM_select=widgets.IntSlider(value=10,min=1,max=30,step=1,description='Smoothing:')                              # Rolling mean window for fig 2             
    CO2e_select=widgets.Checkbox(value=True,description='CO2e',disabled=False)                                      # CO2e toggle for fig 4
    CO2_select=widgets.Checkbox(value=True,description='CO2',disabled=False)                                        # CO2 toggle for fig 2
    SO2_select=widgets.Checkbox(value=True,description='SO2',disabled=False)                                        # SO2 toggle for fig 2
    NOX_select=widgets.Checkbox(value=True,description='NOX',disabled=False)                                        # NOX toggle for fig 2
    CO2_select2=widgets.Checkbox(value=False,description='CO2',disabled=False)                                      # CO2 toggle for fig 4
    SO2_select2=widgets.Checkbox(value=False,description='SO2',disabled=False)                                      # SO2 toggle for fig 4
    NOX_select2=widgets.Checkbox(value=False,description='NOX',disabled=False)                                      # NOX toggle for fig 4
    eff_select=widgets.Checkbox(value=True,description='Efficiency',disabled=False)                                 # Efficiency toggle for fig 4
    CapFac_select=widgets.Checkbox(value=True,description='Capacity Factor',disabled=False)                         # Capacity Factor toggle for fig 4
    Nplot_select=widgets.IntSlider(value=2,min=2,max=8,step=1,description='#years:')                                # Number of years to plot for fig 3
    CO2scale_select=widgets.FloatSlider(value=2.0,min=1.0, max=10.0, step=0.5, description='C02 scaling:')          # y axis control for fig 3
    SO2scale_select=widgets.FloatSlider(value=2.0,min=1.0, max=10.0, step=0.5, description='S02 scaling:')          # y axis control for fig 3

    # Run each plot function using the interact function (and generate text explanations)
    # plot 1
    printmd('## Visualization 1: Generation Boxplots')
    printmd('This plot displays the boxplot of gross generation for each month of the year. It can provide insight regarding the usage of the plant (through the value of the mean) as well as how regular or irregular it is (through the span of the whiskers).')
    printmd('You may choose below the time range to display.')
    interact(CF_boxplot,plantName=fixed(plantName),unitName=fixed(unitName),data=fixed(data),yearRange=year_select)
    # plot 2
    printmd('## Visualization 2: Emissions Time Series')
    printmd('This plot displays a time series of CO2, SO2, and NOx emissions. It tells a story of how the emissions of a unit changes over time. This can provide insights about upgrades, maintenance, extreme events, etc. The values in this plot are normalized by the average for hourly emissions of each gas.')
    printmd('Below, you may choose the time range to display as well as how much smoothing to apply (this performs an average over the number of days chosen). You may also choose which emissions to display. ')
    interact(Norm_Em,plantName=fixed(plantName),unitName=fixed(unitName), data=fixed(data), yearRange=year_select, RM_window=RM_select,CO2_on=CO2_select,SO2_on=SO2_select,NOX_on=NOX_select)
    # plot 3
    printmd('## Visualization 3: Emissions vs Operations')
    printmd('This plot displays emissions intensity versus capacity factor. This shows how emissions change with utilization rates. We expect carbon intensity to be worse at lower capacity factors, but it is interesting to look and see if that is not the case and think about why.')
    printmd('You may choose below the time range to display as well as the number of years. Additionally, you may widen the display window if needed. The scaling value will increase the viewing range on the Y-Axis.')
    interact(EmvCF,plantName=fixed(plantName),unitName=fixed(unitName), data=fixed(data), yearRange=year_select, Nplots=Nplot_select,CO2scale=CO2scale_select,SO2scale=SO2scale_select)
    # plot 4
    printmd('## Visualization 4: Histograms')
    printmd('This section displays a series of histograms of various plant metrics. They show the distribution of time a unit spends operating at various values of these metrics.')
    printmd('You may choose below which histogram to display.')
    interact(emissionHistograms,plantName=fixed(plantName),unitName=fixed(unitName),data=fixed(data),yearRange=year_select,eff_on=eff_select,CapFac_on=CapFac_select,CO2e_on=CO2e_select,CO2_on=CO2_select2,SO2_on=SO2_select2,NOX_on=NOX_select2)

def runDashboard(ev):
    """
    Code executed when the run dashboard button is clicked
    """

    print("Dashboard starting for "+ plantWid.value+ ".")
    # Parse plant and unit name
    plantName=plantWid.value.split(":")[1]
    unitName=plantWid.value.split(":")[2].split(" ")[2]
    # Import Data
    print("Importing data--this can take more than 10 seconds.")
    t_start=time.time()
    data=readDataAWS(plantName, unitName)
    print("Dashboard ready. Time elapsed: " + str(int(time.time()-t_start))+" seconds.")
    # Change data indexing
    data.index=data.DATETIME
    data['Year_Month']=data['OP_DATE'].astype(str).str[:4]+data['OP_DATE'].astype(str).str[5:7]
    data['year']=(data['OP_DATE'].astype(str).str[:4]).astype(int)
    interactive_plots(data,plantName,unitName)

def runDashboardLocal(ev):
    """
    Code executed when the run dashboard local button is clicked
    Not currently implemented (mostly obsolete)
    """
    
    print("Dashboard starting for "+ plantWid.value)
    plantName=plantWid.value.split(":")[1]
    unitName=plantWid.value.split(":")[2].split(" ")[2]
    print("Importing data--this can take more than 10 seconds")
    t_start=time.time()
    data=readDataSmaller(plantName,unitName)
    print("Time elapsed: " + str(np.floor(time.time()-t_start)))
    formatData(data)
    interactive_plots(data,plantName,unitName)

#######################################
##### Section 4 : Notebook Launch #####
#######################################

# The code below this point is executed when this filed is called in the notebook

# Plant and unit selector related code
# First import plant/unit list from csv file
plant_names=pd.read_csv('all_plants_dashboard.csv')
plant_names['state_name_unit']=plant_names['state']+':'+plant_names['name']+': Unit '+plant_names['unitid']
plant_list=plant_names['state_name_unit']
pl=plant_list.tolist()	

plantWid=widgets.Select(
    options=pl,
    value=pl[0],    #Number in brack default initial value. [844] for Jim Bridger (often used in development)
    description='Plant:',
    layout={'width': 'initial'},
    disabled=False
)                                   # The widget is now created

printmd('## Choose a Plant and a Unit and click Load Dashboard')
display(plantWid)                   # Display the widget

# "Run dashboard" button related code
button = widgets.Button(description="Load Dashboard")
button.on_click(runDashboard)                                   # May be changed to runDashboardLocal
display(button)