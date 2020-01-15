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
  -z, --zenith zenith Zenith Angle
  -m, --magnitude magnitude    Magnitude
"""

from docopt import docopt
import csv
import math
import pdb

if __name__ == "__main__":
    arguments = docopt(__doc__)
    print("arguments")
    param_file = arguments["<parameters_filename>"]
    save_file = arguments["<save_filename>"]
    print(save_file," is the saved filename")
    use_DB = False
    compute_tar_psf = not arguments["--fast"]

    # Get parameters from file
    if arguments["--bench"]:
        from shesha.supervisor.benchSupervisor import BenchSupervisor as Supervisor
    elif arguments["--brahma"]:
        from shesha.supervisor.canapassSupervisor import CanapassSupervisor as Supervisor
    else:
        from shesha.supervisor.compassSupervisor import CompassSupervisor as Supervisor

    if arguments["--DB"]:
        use_DB = True

    supervisor = Supervisor(param_file, use_DB=use_DB)
    #set variables
    if arguments["--zenith"]:
        z = float(arguments["--zenith"])
        supervisor.config.p_atmos.set_r0(supervisor.config.p_atmos.get_r0() * (math.cos(z * math.pi / 180)) ** 0.6)
        print("Setting (zenith angle compensated) Fried parameter to ",str(supervisor.config.p_atmos.get_r0()),"...")
        supervisor.config.p_geom.set_zenithangle(z) #CHECK
        print("Setting zenith angle to ",str(supervisor.config.p_geom.get_zenithangle()))
    # end of set variables
    #pdb.set_trace()
    if arguments["--magnitude"]:
        m = float(arguments["--magnitude"])
        supervisor.config.p_wfs0.set_gsmag(m)
        print("Setting WFS magnitude to ",str(supervisor.config.p_wfs0.get_gsmag()))
    if arguments["--devices"]:
        supervisor.config.p_loop.set_devices([
                int(device) for device in arguments["--devices"].split(",")
        ])
    if arguments["--generic"]:
        supervisor.config.p_controllers[0].set_type("generic")
        print("Using GENERIC controller...")

    supervisor.initConfig()
    #print("TTcond=",supervisor.config.p_atmos.get_TTcond())
    #pdb.set_trace()

    if arguments["--niter"]:
        supervisor.loop(int(arguments["--niter"]), compute_tar_psf=compute_tar_psf)
    else:
        supervisor.loop(supervisor.config.p_loop.niter, compute_tar_psf=compute_tar_psf)

    #get variables and write to file
    strehl_all = supervisor.getStrehl(0)
    strehl_le = strehl_all[1]
    row = [arguments["--zenith"], str(strehl_le)]
    with open(save_file, 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)
    csvFile.close()


    #end of get var and write to file
    if arguments["--interactive"]:
        from shesha.util.ipython_embed import embed
        from os.path import basename
        embed(basename(__file__), locals())
