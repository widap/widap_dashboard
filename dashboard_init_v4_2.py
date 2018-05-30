from __future__ import print_function
import matplotlib.pyplot as plt
import matplotlib.cm as cm
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

os.system("jupyter nbextension enable --py widgetsnbextension")
warnings.filterwarnings('ignore')

def readDataSmaller(plantName, unitName):
    #for import from a local file
    con = sq3.connect('smaller.db')

    data = pd.read_sql("select * FROM data WHERE name = '"+plantName+"' AND unitid = '"+unitName+"'", con)

    data['GLOAD']=data['gload']
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


    print("data successfully extracted")

    return data # Will automatically print DataFrame

def readDataAWS(plantName, unitName):
    #from import from the AWS server
    
    server = mysql.connector.connect(user="widap", password="widap123", 
                              host="widapdb-cluster-1.cluster-cpyvkv2lasim.us-west-1.rds.amazonaws.com",
                              database="widap")
#host="widapdb-cluster-1.cluster-cpyvkv2lasim.us-west-1.rds.amazonaws.com"
    query = server.cursor(buffered=True)
    #startdate = datetime.date(2001,1,1)
    #stopdate = datetime.date(2001,1,31)
    query.execute("SELECT STATE,NAME,ORISPL_CODE,UNITID,OP_DATE,OP_HOUR,OP_TIME,GLOAD,op_datetime as DATETIME,SLOAD,SO2_MASS,SO2_RATE,NOX_MASS,NOX_RATE,CO2_MASS,CO2_RATE,HEAT_INPUT FROM wecc WHERE NAME = '{}' AND UNITID = '{}'".format(plantName,unitName))
    #query.execute("  SELECT `plants`.`STATE` AS `STATE`,`plants`.`ORISPL_CODE` AS `ORISPL_CODE`,adddate(`data`.`OP_DATE`,interval `data`.`OP_HOUR` hour) as DATETIME,`plants`.`UNITID` AS `UNITID`,`systems`.`name` AS `SYSTEM`,`plants`.`NAME` AS `NAME`,`plants`.`YEAR` AS `YEAR`,`plants`.`COUNTY` AS `COUNTY`,`plants`.`LATITUDE` AS `LATITUDE`,`plants`.`LONGITUDE` AS `LONGITUDE`,`plants`.`OWNER` AS `OWNER`,`plants`.`OPERATOR` AS `OPERATOR`,`plants`.`PRIMARY_REP` AS `PRIMARY_REP`,`plants`.`SECONDARY_REP` AS `SECONDARY_REP`,`plants`.`PRIMARY_FUEL` AS `PRIMARY_FUEL`,`plants`.`SECONDARY_FUEL` AS `SECONDARY_FUEL`,`data`.`OP_DATE` AS `OP_DATE`,`data`.`OP_HOUR` AS `OP_HOUR`,`data`.`OP_TIME` AS `OP_TIME`,`data`.`GLOAD` AS `GLOAD`,`data`.`SLOAD` AS `SLOAD`,`data`.`SO2_MASS` AS `SO2_MASS`,`data`.`SO2_RATE` AS `SO2_RATE`,`data`.`NOX_RATE` AS `NOX_RATE`,`data`.`NOX_MASS` AS `NOX_MASS`,`data`.`CO2_MASS` AS `CO2_MASS`,`data`.`CO2_RATE` AS `CO2_RATE`,`data`.`HEAT_INPUT` AS `HEAT_INPUT` FROM((`plants` JOIN `data` ON (((`plants`.`STATE` = `data`.`STATE`) AND (`plants`.`YEAR` = YEAR(`data`.`OP_DATE`)) AND (`plants`.`ORISPL_CODE` = `data`.`ORISPL_CODE`) AND (`plants`.`UNITID` = `data`.`UNITID`)))) JOIN `systems` ON ((`plants`.`SYSTEM` = `systems`.`system`))) WHERE (`plants`.`SYSTEM` = 1) AND `plants`.`NAME` = '{}' AND `plants`.`UNITID` = '{}'".format(plantName,unitName))
    data = pd.DataFrame(data=query.fetchall(), index = None, columns = query.column_names)   

    query.close()
    server.close()

    data.columns = data.columns.astype(str) #Solves issue where columns names where bytes and not str

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

    #data['CO2I_gl'].replace('', 0, inplace=True)
    #data['CO2I_ht'].replace('', 0, inplace=True)
    data.sort_values(by=['DATETIME'],inplace=True)


    print("data successfully extracted")
    
    return data # Will automatically print DataFrame

def formatData(data):
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

def CF_boxplot(data,yearRange):
    printmd('## Visualization 1: Generation Boxplots')
    printmd('This plot displays the boxplot of gross generation for each month of the year. It provides both an idea of the usage of the plant (through the value of the mean) as well as how regular or irregular it is (through the span of the whiskers).')
    printmd('You may choose below the time range to display.')
    startYear=yearRange[0]
    endYear=yearRange[1]

	# Make list of plant characteristics for which we want boxplots
    attribute='GLOAD'

    # Make dictionary for chart names
    plantCharNames = {'GLOAD':"Gross Generation [MWh]"}

    boxprops = dict(linestyle='-', linewidth=1, color='k')
    medianprops = dict(linestyle='-', linewidth=3, color='k')
    plt.figure(2)
    bp = data.boxplot(column=attribute,by='Year_Month',showfliers=False,figsize=(24,8),widths = 0.2,boxprops=boxprops, medianprops=medianprops,return_type='dict')
    #axis1 = plt.axes()
    #x_axis = axis1.axes.get_xaxis()
    plt.title("Boxplot of "+plantCharNames[attribute],Fontsize=24)
    plt.suptitle("")
    plt.xlabel('Year',Fontsize=16)
    plt.xticks([1, 13, 25, 37, 49, 61, 73, 85, 97, 109, 121, 133, 145, 157, 169, 183, 195], ['2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011', '2012', '2013', '2014', '2015', '2016','2017'])
    plt.ylabel(plantCharNames[attribute],Fontsize=16)
    plt.xlim((startYear-2001)*12+1,(endYear+1-2001)*12+1)
    plt.show()

def Norm_Em(data,yearRange,RM_window,CO2_on,SO2_on,NOX_on):
    printmd('## Visualization 2: Emissions Time Series')
    printmd('This plot displays a time series of CO2, SO2, and NOx emissions. It tell a story of how the emissions of a unit changes over time. Leads to insights about upgrades, maintenance, extreme events, etc.')
    printmd('You may choose below the time range to display as well as how much smooting to apply (it performs an average over the number of days chosen. You may also chose which emission to display.	')
    startYear=yearRange[0]
    endYear=yearRange[1]
    RM_window=24*RM_window
    leg=[]
    CO=pd.Series.rolling(data['CO2_MASS']/data['CO2_MASS'].mean(), window=RM_window,min_periods=min(3,RM_window)).mean()
    SO=pd.Series.rolling(data['SO2_MASS']/data['SO2_MASS'].mean(), window=RM_window,min_periods=min(3,RM_window)).mean()
    NO=pd.Series.rolling(data['NOX_MASS']/data['NOX_MASS'].mean(), window=RM_window,min_periods=min(3,RM_window)).mean()
    plt.figure(2,figsize=(24,8))
    if CO2_on:
    	plt.plot(CO[str(startYear):str(endYear)],linewidth=0.7)
    	leg.append('CO2')
    if SO2_on:
    	plt.plot(SO[str(startYear):str(endYear)],linewidth=0.7)
    	leg.append('SO2')
    if NOX_on:
    	plt.plot(NO[str(startYear):str(endYear)],linewidth=0.7)
    	leg.append('NOX')
    plt.xlabel('Time',Fontsize=16)
    plt.ylabel('Normalized Emissions',Fontsize=16)
    plt.legend(leg,fontsize=16)
    plt.title('Rolling Mean of Normalized Emissions',Fontsize=24)
	#plt.ylim(0,2.5)
    plt.show()
	#

def EmvCF(data,yearRange,Nplots,CO2range,SO2range):
    printmd('## Visualization 3: Emissions vs Operations')
    printmd('This plot displays emissions intensity against capacity factor. It paints a picture of how emissions change with utilization rates. We expect carbon intensity to be worse at lower capacity factors, but it is interesting to look and see if that is not the case and think about why.')
    printmd('You may choose below the time range to display as well as the number of years. Additionally, you may widen the display window as these vary greatly to one plant to the next.')
    startYear=yearRange[0]
    endYear=yearRange[1]
    yearsToPlot = np.linspace(startYear,endYear,Nplots).astype(int)
    ii=1
    plt.figure(1,figsize=(24,8))
    for ii in range(Nplots):
        year=yearsToPlot[ii]
        plt.subplot(1,2,1)
        plt.plot(data[data['year']==year]['capacityFactor_gl'],data[data['year']==year]['CO2I_gl'],'.', markersize=3)
        plt.title('CO2I vs CF by Generation for requested years',Fontsize=24)
        plt.ylim(CO2range[0],CO2range[1])
        plt.ylabel('CO2I [kg/MWh]',fontsize=16)
        plt.xlabel('Capacity Factor',fontsize=16)
        plt.subplot(1,2,2)
        plt.plot(data[data['year']==year]['capacityFactor_gl'],data[data['year']==year]['SO2I_gl'],'.', markersize=3)
        plt.title('SO2I vs CF by Generation for requested years',Fontsize=24)
        plt.ylim(SO2range[0],SO2range[1])
        plt.ylabel('SO2I [kg/MWh]',fontsize=16)
        plt.xlabel('Capacity Factor',fontsize=16)
    plt.legend(yearsToPlot,fontsize=16)
    plt.show()

def plantEfficiency(data):
        
    heatRate = (data['HEAT_INPUT'] * 1e6) / (data['OP_TIME'] * data['GLOAD'] * 1e3)
    efficiency = (data['OP_TIME'] * data['GLOAD']) / (data['HEAT_INPUT'] * 0.29307107)
    
    #weirdEff = efficiency[efficiency > 1.0]
    #print("There are " + str(weirdEff.size) + " efficiencies higher than 1.")
    #weirdHeatRate = heatRate.index(heatRate) # Figure out how to append to DataFrame
    
    # f7: Plant Characteristics
    plt.figure(4,figsize=(24,8))
    # efficiency
    plt.hist(efficiency,60,[0,0.6])
    plt.xlabel('Efficiency []',fontsize=16)
    plt.ylabel('Freqs',fontsize=16)
    plt.subplots_adjust(wspace = 0.5)
    plt.title('Histogram of Observed Efficiency Values',fontsize=24)
    plt.show() # Just use once, at the bottom of the script

def emissionHistograms(data,eff_on,CapFac_on,CO2e_on,CO2_on,SO2_on,NOX_on):
    printmd('## Visualization 4: Histograms')
    printmd('This section diplays a series of histograms of various plant metrics. They show the distribution of time a unit spends operating at various values of these metrics. They are another way to look at operations of a unit.')
    printmd('You may choose below which histogram to display.')
    
    heatRate = (data['HEAT_INPUT'] * 1e6) / (data['OP_TIME'] * data['GLOAD'] * 1e3)
    efficiency = (data['OP_TIME'] * data['GLOAD']) / (data['HEAT_INPUT'] * 0.29307107)
    
    #weirdEff = efficiency[efficiency > 1.0]
    #print("There are " + str(weirdEff.size) + " efficiencies higher than 1.")
    #weirdHeatRate = heatRate.index(heatRate) # Figure out how to append to DataFrame
    
    # f7: Plant Characteristics
    if eff_on:
    	plt.figure(6,figsize=(24,6))
    	plt.hist(efficiency,100,[0,1.0], density=True)
    	plt.xlabel('Efficiency',fontsize=16)
    	plt.ylabel('Freqs',fontsize=16)
    	plt.title('Histogram of Observed Efficiency Values',Fontsize=24)
    	plt.show() # Just use once, at the bottom of the script

    # f10: Capacity Factor Histogram
    if CapFac_on:
    	plt.figure(6,figsize=(24,6))
    	plt.suptitle('Capacity Factor Histogram', fontsize=24)
    	plt.subplot(121)
    	plt.hist(data['capacityFactor_ht'].dropna(), 100, facecolor='y',log=False, density=True)
    	plt.ylabel('Frequency',fontsize=16)
    	plt.xlabel('Capacity Factor from Heat Input',fontsize=16)
    	plt.subplot(122)
    	plt.hist(data['capacityFactor_gl'].dropna(), 100, facecolor='y',log=False, density=True)
    	plt.ylabel('Frequency',fontsize=16)
    	plt.xlabel('Capacity Factor from Generation',fontsize=16)
    	plt.subplots_adjust(wspace = 0.5)
    	plt.show()

    if CO2e_on:
    	plt.figure(5,figsize=(24,6))
    	plt.suptitle('CO2eI Heat Input Histogram', fontsize=24)
    	plt.subplot(121)
    	plt.hist(data['CO2eI_ht'].dropna(), 100, facecolor='g',log=False, density=True)
    	plt.ylabel('Frequency',fontsize=16)
    	plt.xlabel('CO2e Intensity from Heat Input (kg/MWh)',fontsize=16)
    	plt.subplot(122)
    	plt.hist(data['CO2eI_gl'].dropna(), 100, range=[0, 3*data['CO2eI_gl'].median()], facecolor='g',log=False, density=True)
    	plt.ylabel('Frequency',fontsize=16)
    	plt.xlabel('CO2e Intensity from Generation (kg/MWh)',fontsize=16)
    	plt.subplots_adjust(wspace = 0.5)
    	plt.show()


    # f8: CO2I Histogram
    if CO2_on:
	    plt.figure(5,figsize=(24,6))
	    plt.suptitle('CO2I Heat Input Histogram', fontsize=24)
	    # CO2I by heat
	    plt.subplot(121)
	    plt.hist(data['CO2I_ht'].dropna(), 100, facecolor='g',log=False, density=True)#range=[54, 58],
	#     plt.xlim(0,200)
	    plt.ylabel('Frequency',fontsize=16)
	    plt.xlabel('CO2 Intensity from Heat Input (kg/MWh)',fontsize=16)
	    # CO2I by gross load
	    plt.subplot(122)
	    plt.hist(data['CO2I_gl'].dropna(), 100, range=[0, 3*data['CO2I_gl'].median()], facecolor='g',log=False, density=True)
	#     plt.xlim(0,200)
	    plt.ylabel('Frequency',fontsize=16)
	    plt.xlabel('CO2 Intensity from Generation (kg/MWh)',fontsize=16)
	    plt.subplots_adjust(wspace = 0.5)
	    plt.show()

    if SO2_on:
	    plt.figure(5,figsize=(24,6))
	    plt.suptitle('SO2I Heat Input Histogram', fontsize=24)
	    # CO2I by heat
	    plt.subplot(121)
	    plt.hist(data['SO2I_ht'].dropna(), 100, facecolor='g',log=False, density=True)#range=[54, 58],
	#     plt.xlim(0,200)
	    plt.ylabel('Frequency',fontsize=16)
	    plt.xlabel('SO2 Intensity from Heat Input (kg/MWh)',fontsize=16)
	    # CO2I by gross load
	    plt.subplot(122)
	    plt.hist(data['SO2I_gl'].dropna(), 100, range=[0, 3*data['SO2I_gl'].median()], facecolor='g',log=False, density=True)
	#     plt.xlim(0,200)
	    plt.ylabel('Frequency',fontsize=16)
	    plt.xlabel('SO2 Intensity from Generation (kg/MWh)',fontsize=16)
	    plt.subplots_adjust(wspace = 0.5)
	    plt.show()

    if NOX_on:
	    plt.figure(5,figsize=(24,6))
	    plt.suptitle('NOXI Heat Input Histogram', fontsize=24)
	    # CO2I by heat
	    plt.subplot(121)
	    plt.hist(data['NOXI_ht'].dropna(), 100, facecolor='g',log=False, density=True)#range=[54, 58],
	#     plt.xlim(0,200)
	    plt.ylabel('Frequency',fontsize=16)
	    plt.xlabel('NOX Intensity from Heat Input (kg/MWh)',fontsize=16)
	    # CO2I by gross load
	    plt.subplot(122)
	    plt.hist(data['NOXI_gl'].dropna(), 100, range=[0, 3*data['NOXI_gl'].median()], facecolor='g',log=False, density=True)
	#     plt.xlim(0,200)
	    plt.ylabel('Frequency',fontsize=16)
	    plt.xlabel('NOX Intensity from Generation (kg/MWh)',fontsize=16)
	    plt.subplots_adjust(wspace = 0.5)
	    plt.show()

def N_bits(data):
    return np.log(len(data.value_counts()))/np.log(2)

def printmd(string):
    display(Markdown(string))

def interactive_plots(data):
    year_select=widgets.IntRangeSlider(value=[2001, 2017],min=2001,  max=2017, step=1, description='Range:')
    RM_select=widgets.IntSlider(value=10,min=1,max=30,step=1,description='Smoothing:')
    CO2e_select=widgets.Checkbox(value=True,description='CO2e',disabled=False)
    CO2_select=widgets.Checkbox(value=True,description='CO2',disabled=False)
    SO2_select=widgets.Checkbox(value=True,description='SO2',disabled=False)
    NOX_select=widgets.Checkbox(value=True,description='NOX',disabled=False)
    CO2_select2=widgets.Checkbox(value=False,description='CO2',disabled=False)
    SO2_select2=widgets.Checkbox(value=False,description='SO2',disabled=False)
    NOX_select2=widgets.Checkbox(value=False,description='NOX',disabled=False)
    eff_select=widgets.Checkbox(value=True,description='Efficiency',disabled=False)
    CapFac_select=widgets.Checkbox(value=True,description='Capacity Factor',disabled=False)
    #plot 1
    interact(CF_boxplot,data=fixed(data),yearRange=year_select)
    #plot 2
    interact(Norm_Em, data=fixed(data), yearRange=year_select, RM_window=RM_select,CO2_on=CO2_select,SO2_on=SO2_select,NOX_on=NOX_select)
    #plot 3
    interact(EmvCF, data=fixed(data), yearRange=year_select, Nplots=widgets.IntSlider(value=2,min=2,max=8,step=1,description='#years:'),CO2range=widgets.IntRangeSlider(value=[0, 1500],min=0, max=20000, step=500, description='C02 range:'),SO2range=widgets.FloatRangeSlider(value=[0, 5],min=0,  max=15, step=.1, description='S02 Range:'))
    #plot 4
    interact(emissionHistograms,data=fixed(data),eff_on=eff_select,CapFac_on=CapFac_select,CO2e_on=CO2e_select,CO2_on=CO2_select2,SO2_on=SO2_select2,NOX_on=NOX_select2)

def runDashboard(ev):
    plt.close('all')
    print("Dashboard Starting for "+ plantWid.value)
    plantName=plantWid.value.split(":")[1]
    unitName=plantWid.value.split(":")[2].split(" ")[2]
    print("Importing Data, this could take a while")
    t_start=time.time()
    data=readDataAWS(plantName, unitName)
    print("Time ellapsed: " + str(time.time()-t_start))
    data.index=data.DATETIME
    data['Year_Month']=data['OP_DATE'].astype(str).str[:4]+data['OP_DATE'].astype(str).str[5:7]
    data['year']=(data['OP_DATE'].astype(str).str[:4]).astype(int)
    interactive_plots(data)

def runDashboardLocal(ev):
	plt.close('all')
	print("Dashboard Starting for "+ plantWid.value)
	plantName=plantWid.value.split(":")[1]
	unitName=plantWid.value.split(":")[2].split(" ")[2]
	print("Importing Data, this could take a while")
	t_start=time.time()
	data=readDataSmaller(plantName,unitName)
	print("Time ellapsed: " + str(time.time()-t_start))
	formatData(data)
	interactive_plots(data)


plant_names=pd.read_csv('all_plants_dashboard.csv')
plant_names['state_name_unit']=plant_names['state']+':'+plant_names['name']+': Unit '+plant_names['unitid']
plant_list=plant_names['state_name_unit']
pl=plant_list.tolist()	

plantWid=widgets.Select(
    options=pl,
    value=pl[844],
    # rows=10,
    description='Plant:',
    disabled=False
)

printmd('## Choose a Plant and a Unit and click Load Dashboard')

display(plantWid)

#button = widgets.Button(description="Run using local")
#button.on_click(runDashboardLocal)
#display(button)

button2 = widgets.Button(description="Load Dashboard")
button2.on_click(runDashboard)
display(button2)