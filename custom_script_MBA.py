#Import eVOLVER/script functions
import eVOLVER_module
import numpy as np
import os.path

#Import MBA functions for temperature adjustment based on growth-rate
from analyze_data_MBA import get_current_growth_rate
from adjTemp_MBA import adjVialTemp



def test (OD_data, temp_data, vials, elapsed_time, exp_name):
    MESSAGE = "12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,"
    eVOLVER_module.stir_rate(MESSAGE)
        
    control = np.power(2,range(0,32))
    #Calibrated flow rates
    flow_rate = np.array([1.01,1.05,1.06,1.03,1.05,1.04,1.07,1.1,1.03,1.07,1.02,1,0.99,1.04,1.05,1])#ml/sec

    #Volume assumed for dilution events
    volume =  25 #mL

    #Vials to bump up temperature
    vialsToCook=[0,1,2,3,5]

    #### CHANGE HERE!!!!!!  #####
    #set the upper and lower OD thresholds for the vials IN USE, others at arbitrarily large values (e.g. 99999)
    
    lower_thresh = np.array([0.1,0.1,0.1,0.1,0.1,0.1,0.1,99999,99999,99999,99999,99999,99999,99999,99999,99999])
    upper_thresh = np.array([0.2,0.2,0.2,0.2,0.2,0.2,0.2,99999,99999,99999,99999,99999,99999,99999,99999,99999])
    
    #Ex/
    # lower_thresh = np.array([.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,.05,9999999,.05,.05,9999999])
    # upper_thresh = np.array([.15,.15,.15,.15,.15,.15,.15,.15,.15,.15,.15,.15,9999999,.15,.15,9999999])
    
    ###### ###########  ######
    
    time_out =5
    pump_wait = 5; #wait between pumps (min)

    save_path = os.path.dirname(os.path.realpath(__file__))

    for x in vials:

        ODset_path =  "%s/%s/ODset/vial%d_ODset.txt" % (save_path,exp_name,x)
        data = np.genfromtxt(ODset_path, delimiter=',')
        ODset = data[len(data)-1][1]


        OD_path =  "%s/%s/OD/vial%d_OD.txt" % (save_path,exp_name,x)
        data = np.genfromtxt(OD_path, delimiter=',')
        average_OD = 0

        if len(data) > 15:
            for n in range(1,6):
                average_OD = average_OD + (data[len(data)-n][1]/5) #average of 5 most recent ODs 

            #if average OD above the upper threshold and setpoint not lower threshold, record time and setpoint as lower threshold
            if (average_OD > upper_thresh[x]) and (ODset != lower_thresh[x]): 
                text_file = open(ODset_path,"a+")
                text_file.write("%f,%s\n" %  (elapsed_time, lower_thresh[x]))
                text_file.close()
                ODset = lower_thresh[x]
                
    
            #if average OD below (lower + half the difference between the thresholds) and setpoint not lower threshold, record time and setpoint as upper threshold
            if (average_OD < (lower_thresh[x]+(upper_thresh[x] - lower_thresh[x])/2)) and (ODset != upper_thresh[x]):
                text_file = open(ODset_path,"a+")
                text_file.write("%f,%s\n" %  (elapsed_time, upper_thresh[x]))
                text_file.close()
                ODset = upper_thresh[x]
                get_current_growth_rate(x, elapsed_time, exp_name, writeToFile='y')
                if x in vialsToCook:
                    adjVialTemp(x,exp_name, elapsed_time, tempStep=0.1, g_thr_low=0.3, g_thr_high=0.5)

            if average_OD > ODset:
            #dilute to max of 20 mL
                time_in = - (np.log(lower_thresh[x]/average_OD)*volume)/flow_rate[x]

                if time_in > 20:
                    time_in = 20


                MESSAGE = "%s,0,%d," % ("{0:b}".format(control[x]+control[x+16]) , time_in)
                eVOLVER_module.fluid_command(MESSAGE, x, elapsed_time, pump_wait *60, exp_name, time_in, 'n')
                MESSAGE = "%s,0,%d," % ("{0:b}".format(control[x+16]) , time_out)
                #eVOLVER_module.fluid_command(MESSAGE, x, elapsed_time, pump_wait *60, exp_name, time_out,'n')
                eVOLVER_module.fluid_command(MESSAGE, x, elapsed_time, pump_wait *60, exp_name, time_out,'y')

