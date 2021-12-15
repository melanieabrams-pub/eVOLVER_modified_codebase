import numpy as np
import matplotlib.pyplot as plt
import os.path
from g_rate_MBA import g_rate_avg, g_rate_cycle

##Initialize (var presets if running graphing functions from within this script)

vials = list(xrange(1)) #input the number of vials used
exp_name = 'expt_20180717_MBA_copy' #input the folder of the experiment
plot='y'
save = 'y'
show= 'n'

def get_all_growth_rate(vials, exp_name, plot='n'):
    '''calc growth rate for input vials over entire expt, plots if 'y'''
    ##Load data
    print 'Loading data...'
    save_path = os.path.dirname(os.path.realpath(__file__)) #this pulls the folder above the experiment
    dir_path =  "%s/%s" % (save_path,exp_name)

    OD_data=[]
    pump_log_data=[]

    for n in vials:
        #Reads text files into numpy arrays of [time, datapoint]
        od_path= "%s/OD/vial%d_OD.txt" % (dir_path,n)
        odset_path="%s/ODset/vial%d_ODset.txt" % (dir_path,n)
        temp_path ="%s/temp/vial%d_temp.txt" % (dir_path,n)

        with open(od_path, "r") as odFile:
            od=np.loadtxt(odFile, delimiter=',')
        OD_data.append(od)

        with open(odset_path, "r") as odSetFile:
            odset=np.loadtxt(odSetFile, delimiter=',',skiprows=1)
        pump_log_data.append(odset)
        
            
    ## Measure growth rate
    print ' Measure growth rate...'

    g_rate_x=[]
    g_rate_y=[]
    for n in vials: # comment out one of the two following growth rate metrics
        g_rate= g_rate_avg((OD_data[n]), pump_log_data[n]) #function adapted from Brandon -> average growth rate between pump events
        #g_rate = g_rate_exp(OD_data[n]), pump_log[n]) ##not yet translated to python## function adapted from Chris -> growth rate using exponential fits

        g_rate_x.append(g_rate[0])
        g_rate_y.append(g_rate[1])

    if plot=='y':
        plot_growth_rate(g_rate_x, g_rate_y)
    return g_rate_x, g_rate_y

def plot_growth_rate(g_rate_x, g_rate_y,plot_OD=False, subplots='n'):
    ## Plot
    print 'Plotting data...'

    xmax=max(g_rate_x[-1])
    ymax=max(max(g_rate_y))

    xlabel='Time (Hours)'
    xlim=xmax+10
    ylim=1.1*ymax

    for n in xrange(len(vials)):

        #Growth rate data
        plt.figure(1)
        figName="Growth_Rate_data"
        title=figName+": vial " +str(n)
        if subplots=='y':
            plt.subplot(5,3,n+1)
        plt.scatter(g_rate_x[n], g_rate_y[n])
        plt.title(title)
        plt.ylabel("Growth rate (1/Hr)")
        plt.ylim(0,ylim)
        plt.xlim(0, xlim)
        if save== 'y':
            plt.savefig(figName+"_"+exp_name+".pdf", bbox_inches='tight', format='pdf', dpi=1000)
        if show=='y':
            plt.show()

        #OD data
        plt.figure(2)
        figName="OD_Data"
        title=figName+": vial " +str(n)
        if subplots=='y':
            plt.subplot(5,3,n+1)
        plt.plot(OD_data[n][1], OD_data[n][2])
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel("Optical Density")
        plt.ylim(0,1)
        plt.xlim(0, xlim)
        if save== 'y':
            plt.savefig(figName+"_"+exp_name+".pdf", bbox_inches='tight', format='pdf', dpi=1000)
        if show=='y':
            plt.show()
            



def get_current_growth_rate(vial, elapsed_time, exp_name, writeToFile='n'):
    '''
    Inputs:
        vial to measure
        name of experiment (matching folder path)
        last 
    
    Output:
        returns growth rate of most recent dilution cycle
        (if writeToFile 'y'): writes growth rate for dilution cycle in .txt file in growth_rate directory of experiment
    '''
    save_path = os.path.dirname(os.path.realpath(__file__)) 
    dir_path =  "%s/%s" % (save_path,exp_name)

    OD_data=[]
    pump_log_data=[]
    g_rate_data=[]

    #Reads OD and OD-setpoint files into numpy arrays of [time, datapoint]
    od_path= "%s/OD/vial%d_OD.txt" % (dir_path,vial)
    odset_path="%s/ODset/vial%d_ODset.txt" % (dir_path,vial)
    g_rate_path= "%s/growth_rate/vial%d_growth_rate.txt" % (dir_path,vial)

    with open(od_path, "r") as odFile:
        od=np.loadtxt(odFile, delimiter=',')
    OD_data=od
    #OD_data.append(od)

    with open(odset_path, "r") as odSetFile:
        odset=np.loadtxt(odSetFile, delimiter=',',skiprows=1)
    pump_log_data=odset
    #pump_log_data.append(odset)

    #Get OD data points from most recent dilution cycle (between backdilutions)
        #most recent points in log will be:
            #[-1]: the adjustmet it *just* made after backdiluting,
            #[-2]: the adjustment it *just* made to do that backdilution
            #[-3]: the adjustment it made after the previous backdilution
   
    cycle_ODt=[]
    cycle_ODy=[]
        
    if len(pump_log_data)>2:    
        start_last_cycle=pump_log_data[-3][0]
        end_last_cycle=pump_log_data[-2][0]

        if pump_log_data[-3][1]<pump_log_data[-2][1]:
            print "dilution cycle frameshift"
            pump_log_data=pump_log_data[:-1]

        for datapoint in OD_data:
            if start_last_cycle<datapoint[0]<end_last_cycle:
                cycle_ODt.append(datapoint[0])
                cycle_ODy.append(datapoint[1])
               
        ## Measure growth rate
        print ' Measure growth rate...'

        g_rate_x, g_rate_y=g_rate_cycle(cycle_ODt, cycle_ODy)
##        print g_rate_x
##        print g_rate_y

        ## Write growth rate
        if writeToFile=='y' and g_rate_y != 'empty':
            text_file = open(g_rate_path, "a+")
            text_file.write("%f,%s\n" %  (g_rate_x, g_rate_y))
            text_file.close()
            
        ##Return growth rate    
        return g_rate_x, g_rate_y

#get_current_growth_rate(0,1244.026300, 'expt_20180824_MBA_copy', writeToFile='y')
