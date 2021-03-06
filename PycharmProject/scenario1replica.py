# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 12:26:21 2017

@author: espenhs
"""

import os  # I use this to work with files
import matplotlib.pyplot as plt  # This is for plotting

import psspy  # Import the psse module
import dyntools  # Import the dynamic simulation module
import redirect  # Module for redirecting the PSS/E output to the terminal
from psse_models import load_models  # The load models

# Define default PSS/E variables
_i = psspy.getdefaultint()
_f = psspy.getdefaultreal()
_s = psspy.getdefaultchar()

# Redirect the PSS/E output to the terminal
redirect.psse2py()

psspy.throwPsseExceptions = True

# Files and folders
os.chdir("..")
cwd = os.getcwd()  # Get the current directory
models = os.path.join(cwd, "Models")  # Name of the folder with the models

# Names of the case files
casefile = os.path.join(models, "Scenario1.sav")
dyrfile = os.path.join(models, "Scenario1.dyr")

# Name of the file where the dynamic simulation output is stored
outputfile = os.path.join(cwd, "output.out")

# Start PSS/E
psspy.psseinit(10000)
#
## Initiation----------------------------------------------------------------------------------------------------------------------------------
psspy.case(casefile)  # Read in the power flow data
psspy.dyre_new([1, 1, 1, 1], dyrfile, "", "", "")

# Convert the loads for dynamic simulation
psspy.cong(0)
psspy.conl(0, 1, 1, [0, 0], [10.0, 10.0, 0.0, 100.0])
psspy.conl(0, 1, 2, [0, 0], [10.0, 10.0, 0.0, 100.0])
psspy.conl(0, 1, 3, [0, 0], [10.0, 10.0, 0.0, 100.0])

# Set the time step for the dynamic simulation
psspy.dynamics_solution_params(realar=[_f, _f, 0.005, _f, _f, _f, _f, _f])

psspy.machine_array_channel([1, 2, 5500])  # Monitor Skien Power (as 5101 Hasle does not have any machine to measure frequency)
psspy.machine_array_channel([2, 7, 5500])  # Monitor Skien Frequency (as 5101 Hasle does not have any machine to measure frequency)

load = load_models.Load(3359)  # Create a load consisting of Ringhals

ierr = psspy.strt(outfile=outputfile)  # Tell PSS/E to write to the output file

# Simulation----------------------------------------------------------------------------------------------------------------------------------

if ierr == 0:
    # nprt: number of time steps between writing to screen
    # nplt: number of time steps between writing to output file
    psspy.run(tpause=0, nprt=0, nplt=0)  # run the simulation
    load.step(1120)  # Do a 1120MW load step in Ringhals
    psspy.run(tpause=120)  # Pause the simulation after 120 seconds


else:
    print(ierr)

# Read the output file
chnf = dyntools.CHNF(outputfile)
# assign the data to variables
sh_ttl, ch_id, ch_data = chnf.get_data()

# Do the plotting
plt.figure(1)
plt.plot(ch_data['time'], ch_data[1])  # Kvilldal Power

plt.figure(2)
plt.plot(ch_data['time'], ch_data[2])  # Kvilldal frequency

plt.show()
