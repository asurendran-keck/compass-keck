
# Test script for checking the scaling factor to reduce the minimum norm between Keck and masked COMPASS CM
# Separate scaling factor for TT, x-slope and y-slope sections of the CM
# Good Strehl when combined with the right gain
import csv
import math
import numpy as np
from numpy import linalg as LA
import struct
import sys
import pdb
from matplotlib import pyplot as plt
from astropy.io import fits
import copy
import cv2

if __name__ == "__main__":
    use_DB = False

    # Get parameters from file
    from shesha.supervisor.compassSupervisor import CompassSupervisor as Supervisor
    param_file = "/home/aodev/asurendran/param/1_recon/scao_sh_20x20_4pix_keck_ngs_ml.py" #CHECK
    supervisor = Supervisor(param_file, use_DB=use_DB)

    supervisor.initConfig()
    cmat_comp = supervisor.getCmat(0)

    subap_mask_keck = np.loadtxt('subap_mask_keck.txt', dtype = 'int', delimiter=',')
    subap_mask_keck_1d = subap_mask_keck.flatten()
    mask_pos = np.where(np.array(subap_mask_keck_1d) == 1)
    mask_pos = np.array(mask_pos)[0,:]
    mask_pos_zero = np.where(np.array(subap_mask_keck_1d) == 0)
    mask_pos_zero = np.array(mask_pos_zero)[0,:]
    recon_array_x = np.zeros((349, 400))
    recon_array_y = np.zeros((349, 400))
    recon_file = open('21Dec0116_noTTfilt.mr', 'rb')
    recon_data = recon_file.read()
    recon_array = struct.unpack("!214016f", recon_data) # where 608*352=214016

    recon_xyxy = np.reshape(recon_array, (352, 608))[0:349, :]
    #recon_xyxy = np.reshape(recon_array, (352, 608))[0:349, :]
    recon_x = copy.deepcopy(recon_xyxy[:,::2])
    recon_y = copy.deepcopy(recon_xyxy[:,1::2])
    cmat_comp_x = copy.deepcopy(cmat_comp[:, 0:400])
    cmat_comp_y = copy.deepcopy(cmat_comp[:, 400:800])
    for i in range(304):
      recon_array_x[:, mask_pos[i]] = recon_x[:, i]
      recon_array_y[:, mask_pos[i]] = recon_y[:, i]
    for i in range(np.shape(mask_pos_zero)[0]):
      cmat_comp_x[:, mask_pos_zero[i]] = np.zeros(349)
      cmat_comp_y[:, mask_pos_zero[i]] = np.zeros(349)
    cmat_keck = np.concatenate((recon_array_x, recon_array_y), axis = 1)
    cmat_comp_cond = np.concatenate((cmat_comp_x, cmat_comp_y), axis = 1)

    cmat_wfs_pos_zero = []
    for i in range(800):
      if np.array_equal(cmat_comp_cond[0:349, i], np.zeros(349)) == True:
          cmat_keck[0:349, i] = np.zeros(349)
    # Find minimum norm for x and y and TT separately

    norm_range = np.arange(0.3,0.6,0.02)
    #norm_range_tt = np.arange(0,50,1)
    norm_ind = 0
    norm_x = np.zeros(norm_range.size)
    norm_y = np.zeros(norm_range.size)
    #norm_tt = np.zeros(norm_range_tt.size)
    for i in norm_range:
        norm_x[norm_ind] = np.linalg.norm((i * recon_array_x[0:349,:])+cmat_comp_x[0:349,:])
        norm_y[norm_ind] = np.linalg.norm((i * recon_array_y[0:349,:])+cmat_comp_y[0:349,:])
        norm_ind = norm_ind + 1;
    norm_ind = 0

    # plt.figure()
    # plt.subplot(311)
    # plt.imshow(cmat_keck)
    # plt.colorbar()
    # plt.title('Keck CM')
    # plt.subplot(312)
    # plt.imshow(-cmat_comp_cond)
    # plt.colorbar()
    # plt.title('Conditioned COMPASS CM')
    # plt.subplot(313)
    # res = cmat_keck + cmat_comp_cond
    # plt.imshow(res)
    # plt.colorbar()
    # plt.title('Residual')

    plt.figure()
    plt.subplot(311)
    plt.plot(norm_range, norm_x)
    plt.title('Norm of the x-slope section')
    plt.xlabel('Scaling factor')
    plt.subplot(312)
    plt.plot(norm_range, norm_y)
    plt.title('Norm of the y-slope section')
    plt.xlabel('Scaling factor')
    plt.subplot(313)
    plt.show()
