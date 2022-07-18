'''
What do I need to do with this code?
[   ] plot the full data in a reasonable time
       [   ] 
[   ] divide in condition dataframes
       [   ] Start time, end plateaux time, end filter off time, condition label 
[   ] compare

'''

import pandas as pd
import matplotlib.pyplot as plt
import datetime 
import time
import numpy as np

# This function returns only the rows in the dataframe between initial and final time of a given set
# Times need to be given as strings in the formate "%Y-%m-%dT%H:%M:%S"
def scupltDataSeries(time0, timeN, timeT, calibrationTime, inflectionTime, referenceAvg, df):
    low__Boundary = time.mktime(datetime.datetime.strptime(time0,"%Y-%m-%dT%H:%M:%S").timetuple()) - calibrationTime
    high_Boundary = time.mktime(datetime.datetime.strptime(timeN,"%Y-%m-%dT%H:%M:%S").timetuple()) - calibrationTime
    turn_offPoint = time.mktime(datetime.datetime.strptime(timeT,"%Y-%m-%dT%H:%M:%S").timetuple()) - calibrationTime
    flatLifetimeAverage = np.mean((df.loc[ ((df['timeElapsed'] <= high_Boundary) & (df['timeElapsed'] > low__Boundary)) ])['Luke_PRM_LIFETIME_F_CV'])
    flatLifetimeStd     = np.std((df.loc[ ((df['timeElapsed'] <= high_Boundary) & (df['timeElapsed'] > low__Boundary)) ])['Luke_PRM_LIFETIME_F_CV'])
    reduced_df = df.loc[ ((df['timeElapsed'] <= high_Boundary) & (df['timeElapsed'] > low__Boundary)) ]
    # Calculate the offset from reference time and bring back the waveform at a comparable time
    timeOffSet     = inflectionTime-turn_offPoint
    lifetimeOffSet = referenceAvg  - flatLifetimeAverage
    reduced_df['timeElapsed'] = reduced_df['timeElapsed'] + timeOffSet
    reduced_df['calibratedLifeTime'] = reduced_df['Luke_PRM_LIFETIME_F_CV'] + lifetimeOffSet 
    return reduced_df, flatLifetimeAverage, flatLifetimeStd





#Read Dataframe
df = pd.read_csv("LILArASe.csv")
#df = pd.read_csv("LILArCoatBoardNew.csv", usecols = ['Date-Time','Luke_PRM_LIFETIME_F_CV'])
# Clear Dataframe from NaNs
df.dropna(inplace=True)
#Calculate the first date
s1 = df['Date-Time'].iloc[0]
# Calculate the start time of the sets
startTime = time.mktime(datetime.datetime.strptime(s1,"%Y-%m-%dT%H:%M:%S").timetuple())
# Use time in a more sensible format (in Seconds and not strings)
timeElapsed = df.apply(lambda x: ( time.mktime(datetime.datetime.strptime(x['Date-Time'],"%Y-%m-%dT%H:%M:%S").timetuple() ) - startTime ), axis=1 )
df['timeElapsed'] = timeElapsed


# For the set with no sample, calculate the time where we turn off the filters
filterTurnOff = "2022-07-05T09:36:34"
referenceInflectionTime = time.mktime(datetime.datetime.strptime(filterTurnOff,"%Y-%m-%dT%H:%M:%S").timetuple() ) - startTime
referenceAvg = 0


NoSample_StartDataTaking = df['Date-Time'].iloc[0]
NoSample_filterTurnOff   = "2022-07-05T09:36:34"
NoSample_StopDataTaking  = "2022-07-07T08:06:17"
df1, referenceAvg, refStd = scupltDataSeries(NoSample_StartDataTaking, NoSample_StopDataTaking, NoSample_filterTurnOff, startTime, referenceInflectionTime, referenceAvg, df)

SampleInAirLock_filterTurnOff   = "2022-07-11T09:30:01"
SampleInAirLock_StartDataTaking = "2022-07-09T11:22:46"
SampleInAirLock_StopDataTaking  = "2022-07-12T11:08:31"
df2, Avg2, Std2  = scupltDataSeries(SampleInAirLock_StartDataTaking, SampleInAirLock_StopDataTaking, SampleInAirLock_filterTurnOff, startTime, referenceInflectionTime, referenceAvg, df)


SampleInUllage_filterTurnOff   = "2022-07-13T09:23:35"
SampleInUllage_StartDataTaking = "2022-07-12T20:20:46"
SampleInUllage_StopDataTaking  = df['Date-Time'].iloc[-1]
df3, Avg3, Std3  = scupltDataSeries(SampleInUllage_StartDataTaking, SampleInUllage_StopDataTaking, SampleInUllage_filterTurnOff, startTime, referenceInflectionTime, referenceAvg, df)


fig, (ax1,ax) = plt.subplots(1,2, figsize=(10, 6), gridspec_kw={'width_ratios': [1, 3]})
ax.scatter(x = df1['timeElapsed'], y = df1['Luke_PRM_LIFETIME_F_CV'],label="No Sample")
ax.scatter(x = df2['timeElapsed'], y = df2['calibratedLifeTime']    ,label="Sample in Airlock")
ax.scatter(x = df3['timeElapsed'], y = df3['calibratedLifeTime']    ,label="Sample in Ullage")
ax.legend()
ax.set(xlabel='Time From Start [s]', ylabel='Calibrated Lifetime [s]')


ax1.errorbar([0],[referenceAvg],xerr=[0.1], yerr=[refStd], label="No Sample"        ,marker="o", markersize=10)
ax1.errorbar([0],[Avg2]        ,xerr=[0.1], yerr=[Std2]  , label="Sample in Airlock",marker="o", markersize=10)
ax1.errorbar([0],[Avg3]        ,xerr=[0.1], yerr=[Std3]  , label="Sample in Ullage" ,marker="o", markersize=10)

ax1.legend(loc='lower center')
ax1.set(xlabel='', ylabel='Avg Stable Lifetime, Raw Reading [s]')
ax1.set_ylim(0, 0.007)
plt.setp(ax1.get_xticklabels(), visible=False)
plt.tight_layout()

plt.show()

print(df.keys()) 
