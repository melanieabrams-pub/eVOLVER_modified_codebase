import numpy as np

def g_rate_avg(OD_data, pump_log): # calculate average growth rate between pump events
    ''' This function will split data across MULTIPLE cycles into pump events and return growth rates alog with dil times
        Inputs:
        OD_data = [time, OD]
        pump_log = [time, OD]

        Output:
        g_rate = [times], [growth rates]
        where times are times at dilution and growth rates are for that whole dilution cycle'''
    g_rate_x=[]
    g_rate_y=[]
    for m in xrange(1,len(pump_log)): #iterate through number of pump_log time points after the first event
        if pump_log[m][1] < pump_log[m-1][1]: #if the pump event is a lower threshold
            if pump_log[m][0] - pump_log[m-1][0]>0.1: # if the difference in timepoints is >0.1
                
                #Split OD to each dilution cycle
                ODy=[] #ODs through dilution cycle
                ODt=[] #time points
                ODx=[] #time since beginning of cycle
                
                for element in xrange(len(OD_data)): #if between previous and next cycle, fill in the ODy,t,x
                    if OD_data[element][0]>pump_log[m-1][0]: 
                        if OD_data[element][0]<pump_log[m][0]:
                            ODy.append(OD_data[element][1])
                            ODt.append(OD_data[element][0])

                            cycleStart=ODt[0]
                            for timept in xrange(len(ODt)):
                                ODx.append(ODt[timept]-cycleStart)

                if len(ODx)> 10: # if >10 timepoints, take the mean of the first and last 5 ODs, ignoring NaN and calculate gRate
                    od_end=np.nanmean(ODy[-6:-1])
                    od_start=np.nanmean(ODy[0:5])
                    duration=ODx[-1]
                    rate=1/(duration/np.log(od_end/od_start))
                    g_rate_x.append(ODt[0])
                    g_rate_y.append(rate)

    return g_rate_x, g_rate_y


def g_rate_cycle(ODt,ODy):
    '''
    Inputs:
        ODt: time points from dil cycle
        ODy: ODs from dil cycle
    
    Output:
        writes growth rate for MOST RECENT dilution cycle in .txt file in growth_rate directory of experiment
    '''

    g_rate_x=[]
    g_rate_y=[]

    ODx=[] #time since beginning of cycle
    for timept in xrange(len(ODt)):
        ODx.append(ODt[timept]-ODt[0])

    g_rate_x=ODt[0]
    if len(ODx)> 10: # if >10 timepoints, take the mean of the first and last 5 ODs, ignoring NaN and calculate gRate
        od_end=np.nanmean(ODy[-6:-1])
        od_start=np.nanmean(ODy[0:5])
        duration=ODx[-1]
        rate=1/(duration/np.log(od_end/od_start))
        g_rate_y=rate
        return g_rate_x, g_rate_y

    return g_rate_x, 'empty'
