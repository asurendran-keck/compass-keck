import shesha.config as conf

simul_name = "keck_mode1"

# loop
p_loop = conf.Param_loop()

p_loop.set_niter(10000)
p_loop.set_ittime(0.001)  # =1/1000

# geom
p_geom = conf.Param_geom()
p_geom.set_pupdiam(1000)
p_geom.set_zenithangle(0.)

# tel
p_tel = conf.Param_tel()
p_tel.set_type_ap("keck") # Aperture type
p_tel.set_diam(10.96)
p_tel.set_cobs(0.2356)
p_tel.set_spiders_type("six") # Number of spiders
p_tel.set_pupangle(0) # Pupil rotation angle
p_tel.set_t_spiders(0.0254) # Spiders width in meters
p_tel.set_gap(0.003) # Gap between each segments in meters
p_tel.set_referr(0.000001) # Std of reflectivity error over the segments
p_tel.set_std_tt(0.000001) # Std of tip-tilt aberration over the segments microns
p_tel.set_std_piston(0.000001) # Std of piston aberration over the segments microns
# atmos
p_atmos = conf.Param_atmos()

p_atmos.set_r0(0.16)
p_atmos.set_nscreens(7) # Number of atmospheric layers
p_atmos.set_frac([0.517,0.119,0.063,0.061,0.105,0.081,0.054]) # Fraction out of 1.0
alt_list=[0.1,0.5,1,2,4,8,16]
alt_list = [i * 1000 for i in alt_list]
p_atmos.set_alt(alt_list) # Altitude of the layer in metres
p_atmos.set_windspeed([6.8,6.9,7.1,7.5,10.0,26.9,18.5]) # Windspeed of the layers in m/s
p_atmos.set_winddir([0,90,45,270,240,22.5,180]) # Wind direction in degrees wrt N?
p_atmos.set_L0([25])

# target
p_target = conf.Param_target()
p_targets = [p_target]

# p_target.set_ntargets(1)
p_target.set_xpos(0.)
p_target.set_ypos(0.)
p_target.set_Lambda(1.65)
p_target.set_mag(0.)

# wfs
p_wfs0 = conf.Param_wfs()
p_wfs4 = conf.Param_wfs()
p_wfss = [p_wfs0,p_wfs4]

p_wfs0.set_type("sh")
p_wfs0.set_nxsub(20)
p_wfs0.set_npix(4)
p_wfs0.set_pixsize(1.5)
p_wfs0.set_fracsub(0.5)
p_wfs0.set_xpos(0.)
p_wfs0.set_ypos(0.)
p_wfs0.set_Lambda(0.589)
p_wfs0.set_gsmag(13) # In Sec 5.2.8 from KAON 1240 # CHECK (should be changed to 7.5)
p_wfs0.set_optthroughput(0.36) #In Table 14 from KAON 1240
p_wfs0.set_zerop(1.e11)
p_wfs0.set_noise(-1) # CHECK NOISELESS
p_wfs0.set_atmos_seen(1)

# LBWFS (only for LGS)
#p_wfs1.set_type("sh")
#p_wfs1.set_is_low_order(True)
#p_wfs1.set_nxsub(20)
#p_wfs1.set_npix(16)
#p_wfs1.set_pixsize(0.148) # Confirm (from KAON 265)
#p_wfs1.set_fracsub(0) # According to Florian mail for LO WFS
#p_wfs1.set_xpos(0.)
#p_wfs1.set_ypos(0.)
#p_wfs1.set_Lambda(0.658)
#p_wfs1.set_gsmag(13.)
#p_wfs1.set_optthroughput(0.5)
#p_wfs1.set_zerop(1.e11)
#p_wfs1.set_noise(7.65)
#p_wfs1.set_atmos_seen(1)
# lgs parameters
p_wfs0.set_gsalt(90*1.e3) # From KAON 1240
p_wfs0.set_lltx(0)
p_wfs0.set_llty(0)
p_wfs0.set_laserpower(20) # From Keck TOPTICA specs
p_wfs0.set_lgsreturnperwatt(60.5) # Converted from Mph/m^2/s in Sec 5.2.8 from KAON 1240
#p_wfs0.set_proftype("gauss")
p_wfs0.set_beamsize(1.7) # From K2 LGS AO metrics in Sec 5.3.1 from KAON 1240

p_wfs4.set_type("sh")
p_wfs4.set_is_low_order(True)
p_wfs4.set_nxsub(1)
p_wfs4.set_npix(2)
p_wfs4.set_pixsize(1.4) # from KAON 1069
p_wfs4.set_fracsub(0) # According to Florian mail for LO WFS
p_wfs4.set_xpos(0.)
p_wfs4.set_ypos(0.)
p_wfs4.set_Lambda(0.658)
p_wfs4.set_gsmag(13.)
p_wfs4.set_optthroughput(0.32)
p_wfs4.set_zerop(1.e11)
p_wfs4.set_noise(-1) # 400e/pixel/s translates to 0.4e/pixel/frame at 1000 frames/sec
p_wfs4.set_atmos_seen(1)

# dm
p_dm0 = conf.Param_dm()
p_dm1 = conf.Param_dm()
p_dms = [p_dm0, p_dm1]
p_dm0.set_type("pzt")
nact = p_wfs0.nxsub + 1
p_dm0.set_nact(nact)
p_dm0.set_alt(0.)
p_dm0.set_thresh(0.14)
p_dm0.set_coupling(0.1456)
p_dm0.set_unitpervolt(0.4) # From Wirth ppt on Xinetics DM (max stroke/ max voltage)
p_dm0.set_push4imat(1.) # same as above (max voltage is 65 V)

# Remove DTT mirror for initial simulation (but the TTM is there for Mode 1 Keck)
p_dm1.set_type("tt")
p_dm1.set_alt(0.)
p_dm1.set_unitpervolt(0.016) # unedited
p_dm1.set_push4imat(10.) # unedited

# centroiders
p_centroider0 = conf.Param_centroider()
p_centroider1 = conf.Param_centroider()
p_centroiders = [p_centroider0,p_centroider1]

p_centroider0.set_nwfs(0)
p_centroider0.set_type("cog")
p_centroider1.set_nwfs(0)
p_centroider1.set_type("cog")
# p_centroider0.set_type("corr")
# p_centroider0.set_type_fct("model")

# controllers
p_controller0 = conf.Param_controller()
p_controllers = [p_controller0]

p_controller0.set_type("ls") # Confirm whether this is the correct controller
p_controller0.set_nwfs([0,1])
p_controller0.set_ndm([0,1])
p_controller0.set_maxcond(1500.)
p_controller0.set_delay(1.)
p_controller0.set_gain(0.2)

#p_controller0.set_modopti(0)
#p_controller0.set_nrec(2048)
#p_controller0.set_nmodes(216)
#p_controller0.set_gmin(0.001)
#p_controller0.set_gmax(0.5)
#p_controller0.set_ngain(500)
