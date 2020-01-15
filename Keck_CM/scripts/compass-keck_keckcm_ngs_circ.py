#!/usr/bin/env python
## @package   shesha.script.closed_loop
## @brief     script test to simulate a closed loop (with the Keck NGS Mode)
## @author    COMPASS Team <https://github.com/ANR-COMPASS> and Avinash Surendran
## @version   4.3.0 (COMPASS)
## @date      01/14/2020
## @copyright GNU Lesser General Public License
#
#  This file is part of COMPASS <https://anr-compass.github.io/compass/>
#
#  Copyright (C) 2011-2019 COMPASS Team <https://github.com/ANR-COMPASS>
#  All rights reserved.
#  Distributed under GNU - LGPL
#
#  COMPASS is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser
#  General Public License as published by the Free Software Foundation, either version 3 of the License,
#  or any later version.
#
#  COMPASS: End-to-end AO simulation tool using GPU acceleration
#  The COMPASS platform was designed to meet the need of high-performance for the simulation of AO systems.
#
#  The final product includes a software package for simulating all the critical subcomponents of AO,
#  particularly in the context of the ELT and a real-time core based on several control approaches,
#  with performances consistent with its integration into an instrument. Taking advantage of the specific
#  hardware architecture of the GPU, the COMPASS tool allows to achieve adequate execution speeds to
#  conduct large simulation campaigns called to the ELT.
#
#  The COMPASS platform can be used to carry a wide variety of simulations to both testspecific components
#  of AO of the E-ELT (such as wavefront analysis device with a pyramid or elongated Laser star), and
#  various systems configurations such as multi-conjugate AO.
#
#  COMPASS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
#  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License along with COMPASS.
#  If not, see <https://www.gnu.org/licenses/lgpl-3.0.txt>.
"""
script test to simulate a closed loop

Usage:
  compare_perf_avi.py <parameters_filename> --save_filename <save_filename> [options]

with 'parameters_filename' the path to the parameters file

Options:
  -h --help          Show this help message and exit
  --brahma           Distribute data with BRAHMA
  --bench            For a timed call
  -i, --interactive  keep the script interactive
  -d, --devices devices      Specify the devices
  -n, --niter niter  Number of iterations
  --DB               Use database to skip init phase
  -g, --generic      Use generic controller
  -f, --fast         Compute PSF only during monitoring
  --r0 r0            Fried parameter
  -m, --magnitude magnitude    Magnitude
  -z, --zenith zenith Zenith Angle
  -g --gain gain Controller Gain
"""

from docopt import docopt
import csv
import math
import numpy as np
import struct
import sys
import pdb
from matplotlib import pyplot as plt
from astropy.io import fits
import copy

if __name__ == "__main__":
    # Scaling factor corresponding to the minimum norm for the residual of difference between Keck CM and COMPASS CM (x-slope, y-slope and TT section separate)
    scale_x = -0.46
    scale_y = -0.42
    scale_tt = 23
    # Docopt arguments copied into arguments variable
    arguments = docopt(__doc__)
    print("arguments")
    param_file = arguments["<parameters_filename>"]
    save_file = arguments["<save_filename>"]
    print(save_file," is the saved filename")
    use_DB = False
    compute_tar_psf = not arguments["--fast"]

    # Choose supervisor, COMPASS supervisor default
    if arguments["--bench"]:
        from shesha.supervisor.benchSupervisor import BenchSupervisor as Supervisor
    elif arguments["--brahma"]:
        from shesha.supervisor.canapassSupervisor import CanapassSupervisor as Supervisor
    else:
        from shesha.supervisor.compassSupervisor import CompassSupervisor as Supervisor

    if arguments["--DB"]:
        use_DB = True

    # Initialize supervisor object with parameter file passed as argument
    supervisor = Supervisor(param_file, use_DB=use_DB)

    if arguments["--devices"]:
        supervisor.config.p_loop.set_devices([
                int(device) for device in arguments["--devices"].split(",")
        ])
    if arguments["--generic"]:
        supervisor.config.p_controllers[0].set_type("generic")
        print("Using GENERIC controller...")
    # Custom docopt setters created for COMPASS-Keck. Can be used to set
    # GS mag, ZA and gain. Bash script can be used to check performance
    # by changing these parameters
    if arguments["--magnitude"]:
        supervisor.config.p_wfs0.set_gsmag(float(arguments["--magnitude"]))
        print("Setting magnitude to ", str(supervisor.config.p_wfs0.get_gsmag()),"...")
    if arguments["--zenith"]:
        z = float(arguments["--zenith"])
        supervisor.config.p_atmos.set_r0(supervisor.config.p_atmos.get_r0() * (math.cos(z * math.pi / 180)) ** 0.6)
        print("Setting (zenith angle compensated) Fried parameter to ",str(supervisor.config.p_atmos.get_r0()),"...")
        supervisor.config.p_geom.set_zenithangle(z)
        print("Setting zenith angle to ",str(supervisor.config.p_geom.get_zenithangle()))
    if arguments["--gain"]:
        gain = float(arguments["--gain"])
        supervisor.config.p_controller0.set_gain(gain)
        print("Setting controller gain to ", str(supervisor.config.p_controller0.get_gain()),"...")
    # Initialize the telescope and atmospheric parameters in COMPASS
    supervisor.initConfig()

    # Load Keck subaperture mask
    subap_mask_keck = np.loadtxt('subap_mask_keck.txt', dtype = 'int', delimiter=',')
    subap_mask_keck_1d = subap_mask_keck.flatten()
    mask_pos = np.where(np.array(subap_mask_keck_1d) == 1)
    mask_pos = np.array(mask_pos)[0,:]
    recon_array_x = np.zeros((351, 400))
    recon_array_y = np.zeros((351, 400))
    # Load Keck CM (including TT rows)
    recon_file = open('keck_recon_circ.mr', 'rb')
    recon_data = recon_file.read()
    recon_array = struct.unpack("!214016f", recon_data) # where 608*352=214016
    recon_xyxy = np.reshape(recon_array, (352, 608))[0:351, :]
    # Apply scaling factors to the x-slope, y-slope and TT section of the CM
    recon_x_dm = scale_x * copy.deepcopy(recon_xyxy[0:349,::2])
    recon_y_dm = scale_y * copy.deepcopy(recon_xyxy[0:349,1::2])
    recon_x_tt = scale_tt * copy.deepcopy(recon_xyxy[349:351,::2])
    recon_y_tt = scale_tt * copy.deepcopy(recon_xyxy[349:351,1::2])
    recon_x = np.concatenate((recon_x_dm, recon_x_tt))
    recon_y = np.concatenate((recon_y_dm, recon_y_tt))
    # Incorporate the 304 columns corresponding to x and y slopes of the Keck CM into a 400 column CM with the subaperture mask
    for i in range(304):
      recon_array_x[:, mask_pos[i]] = recon_x[:, i]
      recon_array_y[:, mask_pos[i]] = recon_y[:, i]
    # Final scaled and masked Keck CM to be used for COMPASS
    cmat_keck = np.concatenate((recon_array_x, recon_array_y), axis = 1)

    # Overwrite the CM with scaled and masked Keck CM
    supervisor.setCommandMatrix(cmat_keck)

    #Verification whether recon is used
    recon_check = supervisor.getCmat()
    if np.array_equal(recon_check, cmat_keck) is True:
       print("Command matrix is accepted");
       print("Non zero values in command matrix is ", np.shape(np.nonzero(recon_check))[1])
       print("Size of the command matrix is ", np.shape(recon_check))
    else:
       print("Command matrix is not accepted");

    # Number of AO loop iterations can be passed from the bash script to overwrite the same in the parameter file
    if arguments["--niter"]:
        supervisor.loop(int(arguments["--niter"]), compute_tar_psf=compute_tar_psf)
    else:
        supervisor.loop(supervisor.config.p_loop.niter, compute_tar_psf=compute_tar_psf)

    # supervisor.getStrehl(0)[1] provides the long exposure SR, which together with gain and ZA is written into the CSV file
    strehl_all = supervisor.getStrehl(0)
    strehl_le = strehl_all[1]
    row = [str(supervisor.config.p_geom.get_zenithangle()), str(supervisor.config.p_controller0.get_gain()), str(strehl_le)]
    with open(save_file, 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)
    csvFile.close()
