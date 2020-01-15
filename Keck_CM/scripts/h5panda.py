#!/usr/bin/env python
import numpy as np
import pandas as pd

#Parameter initialization (check with the COMPASS param file)
subap = 20
act = subap + 1
influ_act = 3
center_pos = [5.48, 5.48];
influpix_peract = 10
dm_diameter_pup = [10.96, 10.96]
dm_diameter = [10.96, 10.96]
ccf = 0.1456
act_mask_file = 'act_mask_keck.txt'
pix_res = [dm_diameter[0] / (influpix_peract * act), dm_diameter[0] / (influpix_peract * act)] #m/pix for influence function in terms of DM diameter
influ_start = -((influ_act + 0.5) * influpix_peract)
influ_end = ((influ_act + 0.5) * influpix_peract)
#influ_end = ((influ_act / 2) - 0.5) * influpix_peract
#pos_start = -(dm_diameter[0] / 2)
#pos_end = (dm_diameter[0] / 2)
#unitpervolt = 0.04
ninflu = np.int(influ_end - influ_start)
act_mask_keck = np.loadtxt(act_mask_file, dtype = 'int', delimiter=',')

#Setting actuator positions
#pos = np.array(np.meshgrid(np.linspace(pos_start, pos_end, num = act), np.linspace(pos_start, pos_end, num = act)))
#x_pos = np.reshape(pos[0,:,:], act ** 2)
#y_pos = np.reshape(pos[1,:,:], act ** 2)
y_pos, x_pos = np.where(np.array(act_mask_keck) == 1)
y_pos_m = [i * (dm_diameter[0] / (act - 1)) for i in y_pos]
x_pos_m = [i * (dm_diameter[0] / (act - 1)) for i in x_pos]
y_pos_m = np.array(y_pos_m)
x_pos_m = np.array(x_pos_m)

#Influence function generation (gaussian)
nact = np.shape(x_pos)[0]
influ_mat = np.zeros((ninflu, ninflu, nact))
influ_stddev = influpix_peract / np.sqrt(np.negative(2 * np.log(ccf)))
influ_pos = np.array(np.meshgrid(np.linspace(influ_start, influ_end, num = ninflu), np.linspace(influ_start, influ_end, num = ninflu)))
influ_single = np.exp(np.negative((influ_pos[0,:,:] ** 2) + (influ_pos[1,:,:] ** 2)) / (2 * (influ_stddev ** 2)))
for i in range(nact):
   influ_mat[:,:,i] = influ_single;

#Dictionary columns for dataframe and H5 file write
h5data = {'xpos': x_pos_m,
        'ypos': y_pos_m,
        'center': center_pos,
        'res': pix_res,
        'dm_diam': dm_diameter,
        'dm_diam_pup': dm_diameter_pup,
        'influ': influ_mat}
resAll = pd.DataFrame().append(h5data, ignore_index=True)
resAll.to_hdf('dm_data.h5', key='resAll', mode='w')
