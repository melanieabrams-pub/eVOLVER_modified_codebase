import os.path
import g_rate_MBA
import numpy as np
from analyze_data_MBA import get_all_growth_rate, get_current_growth_rate


def bumpByTime(vials, exp_name, stepUp=0.1):
        '''to call this function every set unit of time,
        import this function in main_eVOLVER
        add the following to custom_functions of main_eVOLVER:

        #custom script to bump up temp, with example setpoints
                # vialsToBumpUp=[0] 
                # hoursTillBump=(6)
                # if int(round(elapsed_time*3600))%(hoursTillBump*3600)<10:
                #     print "calling gRate function"
                #     bumpByTime(vialsToBumpUp,exp_name, stepUp=0.1)
         '''

        save_path = os.path.dirname(os.path.realpath(__file__))
        dir_path =  "%s/%s" % (save_path,exp_name)
        for x in vials:
            tempconfig_path =  "%s/temp_config/vial%d_tempconfig.txt" % (dir_path,x)
            with open(tempconfig_path, "r") as tempfile:
                lines=tempfile.readlines()
                currentTemp=float(lines[1][2:])
                bumpedUpTemp=str(currentTemp+stepUp)
                lines[1]="0,%s\n" % (bumpedUpTemp)
            with open(tempconfig_path, "w") as tempfile:
                for line in lines:
                    tempfile.write(line)
        print "bumped up temperature by" + str(stepUp)
        return
        
def bumpByGRate(vials, exp_name, tempStep=0.1, g_thr_low=0.23, g_thr_high=0.35): #doubling 2-3 hrs is threshold
        '''to call this function every set unit of time, with example setpoints
        import this function in main_eVOLVER
        add the following to custom_functions of main_eVOLVER:

        #custom script to bump up temp
                # vialsToBumpUp=[0]
                # hoursTillBump=(6)
                # if int(round(elapsed_time*3600))%(hoursTillBump*3600)<10:
                #     print "calling gRate function"
                #     bumpByGRate(vialsToBumpUp,exp_name, tempStep=0.1,g_thr_low=0.4, g_thr_high=0.5)
        '''

        ##Load data 
 
        print 'Loading data...'
        save_path = os.path.dirname(os.path.realpath(__file__)) #this pulls the folder above the experiment, so need to take the scripts out of subfolder
        dir_path =  "%s/%s" % (save_path,exp_name)
        for x in vials:
                tempconfig_path =  "%s/temp_config/vial%d_tempconfig.txt" % (dir_path,x)
                print "checking growth rate"
                g_rate_vals=get_all_growth_rate([x], exp_name)[1]
                #g_rate_vals=g_rate.g_rate_avg(pump_log_data[x][0], pump_log_data[x])[1]
                g_rate_end=np.mean(g_rate_vals[-3:]) # look at last 3 dilution cycles when deciding to bump up or down
                print "recent growth rate = "+str(g_rate_end)
                if g_rate_end>g_thr_high:
                    with open(tempconfig_path, "r") as tempfile:
                        lines=tempfile.readlines()
                        currentTemp=float(lines[1][2:])
                        bumpedUpTemp=str(currentTemp+tempStep)
                        lines[1]="0,%s\n" % (bumpedUpTemp)
                    with open(tempconfig_path, "a+") as tempfile:
                            tempfile.write(lines[1])
                    print "bumped up temperature by" + str(tempStep)

        if g_rate_end<g_thr_low:
            with open(tempconfig_path, "r") as tempfile:
                lines=tempfile.readlines()
                currentTemp=float(lines[1][2:])
                bumpedDownTemp=str(currentTemp-tempStep)
                lines[1]="0,%s\n" % (bumpedDownTemp)
            with open(tempconfig_path, "a+") as tempfile:
                    tempfile.write(lines[1])
            print "bumped down temperature by" + str(tempStep)

def adjVialTemp(vial,exp_name, elapsed_time, tempStep=0.1, g_thr_low=0.0, g_thr_high=100.0, numCycleSensitivity=3):

        '''
        Inputs:
                vial to adjust
                name of experiment (matching folder path)
                elapsed time
                
                amount to adjust temperature in vial per step
                lower growth rate threshold (defaults to none)
                upper growth rate threshold (defaults to arbitrarily high)
                number of cyles to look at before making temperature adjustment decision
        Output:
                adjusts temperature setpoint of vial if above or below growth rate threshold
        '''
        save_path = os.path.dirname(os.path.realpath(__file__)) #this pulls the folder above the experiment, so need to take the scripts out of subfolder
        dir_path =  "%s/%s" % (save_path,exp_name)

        tempconfig_path =  "%s/temp_config/vial%d_tempconfig.txt" % (dir_path,vial)
        g_rate_path = "%s/growth_rate/vial%d_growth_rate.txt" % (dir_path,vial)

        g_rates= np.genfromtxt(g_rate_path, delimiter =',')

        average_g_rate= 0
        if len(g_rates)>6:
                for n in range(1,numCycleSensitivity+1):
                        average_g_rate = average_g_rate + (g_rates[len(g_rates)-n][1]/numCycleSensitivity) # average of 3 most recent
                        print g_rates[len(g_rates)-n][1]
        else:
                print "too early to average "+str(numCycleSensitivity)+ " growth rates"
                
        if average_g_rate > g_thr_high and average_g_rate != 0:
                print "average_g_rate > g_thr_high: ", average_g_rate, g_thr_high
                with open(tempconfig_path, "r") as tempfile:
                        lines=tempfile.readlines()
                        lastLine=lines[-1].split(',')
                        currentTemp=float(lastLine[1])
                        bumpedUpTemp=str(currentTemp+tempStep)
                        lines[1]="0,%s\n" % (bumpedUpTemp)
                text_file = open(tempconfig_path, "a+")
                text_file.write("%f,%s\n" %  (elapsed_time, bumpedUpTemp))
                text_file.close()

                print "bumped up vial " +str(vial)+ " temperature by " + str(tempStep) + "C to " + str(bumpedUpTemp) + "C"
                
        if average_g_rate < g_thr_low and average_g_rate != 0:
                print "average_g_rate < g_thr_low: ", average_g_rate, g_thr_high
                with open(tempconfig_path, "r") as tempfile:
                        lines=tempfile.readlines()
                        lastLine=lines[-1].split(',')
                        currentTemp=float(lastLine[1])
                        bumpedDownTemp=str(currentTemp-tempStep)
                        lines[1]="0,%s\n" % (bumpedDownTemp)
                text_file= open(tempconfig_path, "a+")
                text_file.write("%f,%s\n" %  (elapsed_time, bumpedDownTemp))
                text_file.close()

                print "bumped down vial " +str(vial)+ " temperature by " + str(tempStep)+ "C to " + str(bumpedDownTemp) + "C"
                

