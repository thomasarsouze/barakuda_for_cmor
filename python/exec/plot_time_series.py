#!/usr/bin/env python

#       B a r a K u d a
#
#     Generate misc. time-series out of NEMO output files...
#
#       L. Brodeau, 2013
#

import sys
import os
import numpy as nmp

from netCDF4 import Dataset

import barakuda_tool as bt
import barakuda_ncio as bn
import barakuda_orca as bo
import barakuda_plot as bp


Socean = 363.           ; # Surface of the ocean in 10^6 km^2
Lt_1y  = 365.*24.*3600.*1E-6 ; # Length of 1 year in 10^6 seconds (=31.536)

csn = sys.argv[0]

cv_evb = 'evap_ao_cea' ; # debug evap in ec-earth...

DEFAULT_LEGEND_LOC = 'lower left'

venv_needed = {'ORCA','EXP','NN_SST','NN_SSS','NN_SSH','NN_T','NN_S','NN_MLD','LMOCLAT',
               'TRANSPORT_SECTION_FILE','FIG_FORM','BM_FILE'}

vdic = bt.check_env_var(csn, venv_needed)

CONFEXP = vdic['ORCA']+'-'+vdic['EXP']

ff = vdic['FIG_FORM'] ; # format for figures (usually "png" or "svg")


narg = len(sys.argv)
if narg != 2:
    print 'Usage: {} <diag>'.format(csn)
    sys.exit(0)
cdiag = sys.argv[1]

print '\n '+csn+': diag => "'+cdiag+'"'

if cdiag == 'mean_tos':
    cvar  = vdic['NN_SST']
    idfig = 'simple'
    clnm  = 'Globally-averaged sea surface temperature'
    cyu   = r'$^{\circ}$C'
    ym    = yp = 0.

elif cdiag == 'mean_sos':
    cvar  = vdic['NN_SSS']
    idfig = 'simple'
    clnm  = 'Globally-averaged sea surface salinity'
    cyu   = r'PSU'
    ym = yp = 0.

elif cdiag == 'mean_fwf':
    venv_ndd = {'NN_FWF','NN_EMP','NN_RNF','NN_P','NN_CLV','NN_E'}
    vdic_fwf = bt.check_env_var(csn, venv_ndd)
    idfig = 'fwf'
    cvar  = 'EmPmR'
    clnm  = 'Globally-averaged upward net freshwater flux (E-P-R = '+vdic_fwf['NN_FWF']+')'
    cvr2  = 'R'
    cln2  = 'Globally-averaged continental runoffs (R = '+vdic_fwf['NN_RNF']+')'
    cvr3  = 'EmP'
    cln3  = 'Globally-averaged Evaporation - Precipitation (E-P = '+vdic_fwf['NN_EMP']+')'
    cvr4  = 'P'
    cln4  = 'Globally-averaged Precipitation (P = '+vdic_fwf['NN_P']+')'
    cvr5  = 'ICalv'
    cln5  = 'Globally-averaged ice calving from icebergs (ICalv = '+vdic_fwf['NN_CLV']+')'
    cvr6  = 'E'
    cln6  = 'Globally-averaged evaporation (E = '+vdic_fwf['NN_E']+')'
    cvr7  = 'Eb'
    cln7  = 'Globally-averaged evap. t.i.a sea-ice (E = '+cv_evb+')'
    cyu   = r'Sv'
    ym = yp = 0.

elif cdiag == 'mean_htf':
    venv_ndd = {'NN_QNET','NN_QSOL'}
    vdic_htf = bt.check_env_var(csn, venv_ndd)
    idfig = 'htf'
    cvar  = 'Qnet'
    clnm  = 'Globally-averaged net total heat flux to the ocean ('+vdic_htf['NN_QNET']+')'
    cvr2  = 'Qsol'
    cln2  = 'Globally-averaged net solar heat flux to the ocean ('+vdic_htf['NN_QSOL']+')'
    cyu   = r'PW'
    ym = yp = 0.

elif cdiag == 'mean_zos':
    cvar  = vdic['NN_SSH']
    idfig = 'simple'
    clnm  = 'Globally-averaged sea surface height'
    cyu   = r'm'
    ym = yp = 0.

elif  cdiag == '3d_thetao':
    cvar  = vdic['NN_T']
    idfig = 'ts3d'
    clnm = 'Globally-averaged temperature'
    cyu  = r'$^{\circ}$C'
    #ym = 3.6 ; yp = 4.
    ym = 0. ; yp = 0.
    #ym0  = 1.5 ; yp0 = 20.
    ym0  = yp0 = 0.

elif cdiag == '3d_so':
    cvar  = vdic['NN_S']
    idfig = 'ts3d'
    clnm = 'Globally-averaged salinity'
    cyu  = r'PSU'
    #ym  = 34.6 ; yp  = 35.
    #ym0 = 34.6 ; yp0 = 35.
    ym  = yp  = 0.
    ym0 = yp0 = 0.

elif cdiag == 'amoc':
    idfig = 'amoc'
    cyu  = r'Sv'
    ym = 4.5
    yp = 25.5

elif cdiag == 'mean_mld':
    cvar  = vdic['NN_MLD']
    idfig = 'mld'
    clnm  = 'Mean mixed-layer depth, '
    cyu   = r'm'
    ym = yp = 0.

elif cdiag == 'transport_sections':
    idfig = 'transport'
    print '  Using TRANSPORT_SECTION_FILE = '+vdic['TRANSPORT_SECTION_FILE']
    list_sections = bt.get_sections_from_file(vdic['TRANSPORT_SECTION_FILE'])
    print 'List of sections to treat: ', list_sections

elif cdiag == 'seaice':
    idfig = 'ice'
    cyu  = r'10$^6$km$^2$'

else:
    print 'ERROR: '+csn+' => diagnostic '+cdiag+' unknown!'; sys.exit(0)




############################################################# 
# Time series of 2D-averaged  2D fields such as SST, SSS, SSH
#############################################################

if idfig == 'simple':

    cf_in = 'mean_'+cvar+'_'+CONFEXP+'_GLO.nc' ;  bt.chck4f(cf_in, script_name=csn)
    id_in = Dataset(cf_in)
    vtime = id_in.variables['time'][:]
    vvar  = id_in.variables[cvar][:]
    id_in.close()
    (nby, nbm, nbr, ittic) = bt.test_nb_years(vtime, cdiag)

    # Annual data
    VY, FY = bt.monthly_2_annual(vtime[:], vvar[:])

    # Time to plot
    bp.plot("1d_mon_ann")(vtime, VY, vvar, FY, cfignm=cdiag+'_'+CONFEXP, dt=ittic,
                          cyunit=cyu, ctitle = CONFEXP+': '+clnm, ymin=ym, ymax=yp, cfig_type=ff)

    if cvar == vdic['NN_SSH']:
        clnm = 'Global freshwater imbalance based on annual SSH drift'
        Fimb = nmp.zeros(nby)
        for jy in range(1,nby):
            Fimb[jy] = (FY[jy] - FY[jy-1])*Socean/Lt_1y
        Fimb[0] = nmp.nan
        bp.plot("1d_mon_ann")(VY, VY, Fimb, Fimb, cfignm=cdiag+'-imb_'+CONFEXP, dt=ittic,
                              cyunit='Sv', ctitle = CONFEXP+': '+clnm,
                              ymin=-0.8, ymax=0.8, dy=0.1, cfig_type=ff, y_cst_to_add=0.)



############################################################
# Time series of 3D-averaged 3D fields such as SST, SSS, SSH
############################################################

if idfig == 'ts3d':

    vzrange = [ '0-bottom', '0-100'  , '100-1000',   '1000-bottom'  ] ;  nbzrange = len(vzrange)
    vlab    = [ 'AllDepth', '0m-100m', '100m-1000m', '1000m-bottom' ]

    list_basin_names, list_basin_lgnms = bo.get_basin_info(vdic['BM_FILE'])    
    nb_oce = len(list_basin_names)

    joce = 0
    for coce in list_basin_names[:]:
        cf_in = '3d_'+cvar+'_'+CONFEXP+'_'+coce+'.nc' ;  bt.chck4f(cf_in, script_name=csn)
        id_in = Dataset(cf_in)
        vtime = id_in.variables['time'][:]
        if joce == 0: (nby, nbm, nbr, ittic) = bt.test_nb_years(vtime, cdiag)
        jz = 0
        for czr in vzrange:
            if not joce and not jz:
                FM = nmp.zeros((nb_oce, nbzrange, nbr))
            print '   * reading '+cvar+'_'+czr+' in '+cf_in
            FM[joce,jz,:]  = id_in.variables[cvar+'_'+czr][:]
            jz = jz + 1
        id_in.close()

        # Annual data (if makes sence):
        if joce == 0:
            VY = nmp.zeros(nby)
            FY = nmp.zeros((nb_oce, 4, nby))
        if nbm >= 12:
            # the file contains monthly data (nbm=-1 otherwize)
            VY[:], FY[joce,:,:] = bt.monthly_2_annual(vtime[:], FM[joce,:,:])
        else:
            # the file contains annual data
            VY[:]        = vtime[:]
            FY[joce,:,:] = FM[joce,:,:]
            

        print ' *** '+list_basin_lgnms[joce]+' done...\n'
        joce = joce + 1

    # One plot only for global:
    bp.plot("1d_mon_ann")(vtime, VY, FM[0,0,:], FY[0,0,:], cfignm=cdiag+'_'+CONFEXP, dt=ittic,
                          cyunit=cyu, ctitle = CONFEXP+': '+clnm, ymin=ym, ymax=yp, cfig_type=ff)

    # Global for different depth:
    bp.plot("1d_multi")(vtime, FM[0,:,:], vlab[:], cfignm=cdiag+'_lev_'+CONFEXP, dt=ittic,
                        loc_legend='out', cyunit=cyu, ctitle = CONFEXP+': '+clnm, ymin=ym0, ymax=yp0, cfig_type=ff)

    # Show each ocean (All depth):
    bp.plot("1d_multi")(vtime, FM[:,0,:], list_basin_lgnms, cfignm=cdiag+'_basins_'+CONFEXP, dt=ittic,
                        loc_legend='out', cyunit=cyu, ctitle = CONFEXP+': '+clnm, ymin=ym0, ymax=yp0, cfig_type=ff)



#############################################################
# Time series of 2D-average of surface heat flux components
#   - might include IFS (atmosphere) fields when EC-Earth
#############################################################

if idfig == 'htf':

    l_qsr = False
    cf_in = cdiag+'_'+CONFEXP+'_GLO.nc' ;  bt.chck4f(cf_in, script_name=csn)

    id_in = Dataset(cf_in)
    list_var = id_in.variables.keys()
    vtime = id_in.variables['time'][:]
    vqnt  = id_in.variables[cvar][:]
    if cvr2 in list_var[:]:
        l_qsr = True
        vqsr  = id_in.variables[cvr2][:]
    id_in.close()

    (nby, nbm, nbr, ittic) = bt.test_nb_years(vtime, cdiag)

    # Checking if there a potential file for IFS:
    l_htf_ifs = False
    cf_IFS_in = cdiag+'_IFS_'+vdic['EXP']+'_GLO.nc'
    print '  *** Checking for the existence of '+cf_IFS_in
    if os.path.exists(cf_IFS_in):
        print "  *** IFS HTF files found!"
        id_IFS_in = Dataset(cf_IFS_in)
        vqnt_ifs = id_IFS_in.variables['flx_qnet_pw'][:]
        vqsr_ifs = id_IFS_in.variables['flx_ssr_pw'][:]
        id_IFS_in.close()
        if len(vqnt_ifs) != nbm:
            print 'ERROR: '+csn+' => length of E-P of IFS in '+cf_IFS_in+' does not agree with its NEMO counterpart!'
            print '       =>', len(vqnt_ifs), nbm
            sys.exit(0)
        l_htf_ifs = True
    else:
        print '       => Nope!\n'
        
    # Annual data
    VY, FY = bt.monthly_2_annual(vtime, vqnt)
    # Time to plot
    bp.plot("1d_mon_ann")(vtime, VY, vqnt, FY, cfignm=cdiag+'_qnt_'+CONFEXP, dt=ittic,
                          cyunit=cyu, ctitle = CONFEXP+': '+clnm, ymin=ym, ymax=yp, cfig_type=ff)
    if l_qsr:
        VY, FY = bt.monthly_2_annual(vtime, vqsr)
        bp.plot("1d_mon_ann")(vtime, VY, vqsr, FY, cfignm=cdiag+'_qsr_'+CONFEXP, dt=ittic,
                              cyunit=cyu, ctitle = CONFEXP+': '+cln2, ymin=ym, ymax=yp, cfig_type=ff)

    # Only Qnet (NEMO and IFS)
    if l_htf_ifs:
        vlab = [] ; nbd = 2
        Xplt = nmp.zeros((nbd,nbm))
        Xplt[0,:] = vqnt[:]           ; vlab.append('Qnet NEMO ('+vdic_htf['NN_QNET']+')')
        Xplt[1,:] = vqnt_ifs[:]       ; vlab.append('Qnet IFS (SSR+STR+SLHF+SSHF')
        bp.plot("1d_multi")(vtime, Xplt, vlab, cfignm=cdiag+'_qnt_NEMO_IFS_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': Surface net heat flux (monthly)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out')
        # Same but annual:
        Xplt = nmp.zeros((nbd,nby))
        VY, Xplt[0,:] = bt.monthly_2_annual(vtime[:], vqnt[:])
        VY, Xplt[1,:] = bt.monthly_2_annual(vtime[:], vqnt_ifs[:])
        bp.plot("1d_multi")(VY, Xplt, vlab, cfignm=cdiag+'_qnt_NEMO_IFS_annual_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': Surface net heat flux (annual)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out',
                            cinfo='Mean diff = '+str(round(nmp.mean(vqnt[:]-vqnt_ifs[:]),3))+' '+cyu )


    # Only Qnon-solar (NEMO and IFS)
    if l_htf_ifs and l_qsr:
        vlab = [] ; nbd = 2
        Xplt = nmp.zeros((nbd,nbm))
        Xplt[0,:] = vqnt[:] - vqsr[:] ; vlab.append('Qnsol NEMO ('+vdic_htf['NN_QNET']+'-'+vdic_htf['NN_QSOL']+')')
        Xplt[1,:] = vqnt_ifs[:] - vqsr_ifs[:] ; vlab.append('Qnsol IFS (STR+SLHF+SSHF)')
        bp.plot("1d_multi")(vtime, Xplt, vlab, cfignm=cdiag+'_qns_NEMO_IFS_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': Surface net NON-solar flux (monthly)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out')
        # Same but annual:
        Xplt = nmp.zeros((nbd,nby))
        VY, Xplt[0,:] = bt.monthly_2_annual(vtime[:], vqnt[:] - vqsr[:])
        VY, Xplt[1,:] = bt.monthly_2_annual(vtime[:], vqnt_ifs[:] - vqsr_ifs[:])
        bp.plot("1d_multi")(VY, Xplt, vlab, cfignm=cdiag+'_qns_NEMO_IFS_annual_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': Surface net NON-solar flux (annual)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out',
                            cinfo='Mean diff = '+str(round(nmp.mean(vqnt[:]-vqsr[:] - (vqnt_ifs[:]-vqsr_ifs[:])),3))+' '+cyu )


    # Only Qsol (NEMO and IFS)
    if l_htf_ifs and l_qsr:
        vlab = [] ; nbd = 2
        Xplt = nmp.zeros((nbd,nbm))
        Xplt[0,:] = vqsr[:]           ; vlab.append('Qsol NEMO ('+vdic_htf['NN_QSOL']+')')
        Xplt[1,:] = vqsr_ifs[:]       ; vlab.append('Qsol IFS (SSR)')
        bp.plot("1d_multi")(vtime, Xplt, vlab, cfignm=cdiag+'_qsr_NEMO_IFS_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': Surface net solar flux (monthly)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out')
        # Same but annual:
        Xplt = nmp.zeros((nbd,nby))
        VY, Xplt[0,:] = bt.monthly_2_annual(vtime[:], vqsr[:])
        VY, Xplt[1,:] = bt.monthly_2_annual(vtime[:], vqsr_ifs[:])
        bp.plot("1d_multi")(VY, Xplt, vlab, cfignm=cdiag+'_qsr_NEMO_IFS_annual_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': Surface net solar flux (annual)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out',
                            cinfo='Mean diff = '+str(round(nmp.mean(vqsr[:]-vqsr_ifs[:]),3))+' '+cyu )







###################################################################
# Time series of 2D-average of surface freshwater flux components
#   - might include IFS (atmosphere) fields when EC-Earth
###################################################################

if idfig == 'fwf':

    l_rnf = False ; l_emp = False ; l_prc = False ; l_clv = False ; l_evp = False ; l_evb = False
    cf_in = cdiag+'_'+CONFEXP+'_GLO.nc' ;  bt.chck4f(cf_in, script_name=csn)

    id_in = Dataset(cf_in)
    list_var = id_in.variables.keys()
    vtime = id_in.variables['time'][:]
    vfwf  = id_in.variables[cvar][:]
    if cvr2 in list_var[:]:
        l_rnf = True
        vrnf  = id_in.variables[cvr2][:]
    if cvr3 in list_var[:]:
        l_emp = True
        vemp  = id_in.variables[cvr3][:]
    if cvr4 in list_var[:]:
        # There is sometimes Precip in NEMO output which only has NaN! lolo
        l_prc = True ; l_prc_nemo_valid = True
        vprc  = id_in.variables[cvr4][:]
        if nmp.isnan(vprc[0]): l_prc_nemo_valid = False
    if cvr5 in list_var[:]:
        l_clv = True
        vclv  = id_in.variables[cvr5][:]
    if cvr6 in list_var[:]:
        l_evp = True
        vevp  = id_in.variables[cvr6][:]
    if cvr7 in list_var[:]:
        l_evb = True
        vevb  = id_in.variables[cvr7][:]
    id_in.close()

    (nby, nbm, nbr, ittic) = bt.test_nb_years(vtime, cdiag)

    # Checking if there a potential file for IFS:
    l_fwf_ifs = False
    cf_IFS_in = cdiag+'_IFS_'+vdic['EXP']+'_GLO.nc'
    print '  *** Checking for the existence of '+cf_IFS_in
    if os.path.exists(cf_IFS_in):
        print "  *** IFS FWF files found!"
        id_IFS_in = Dataset(cf_IFS_in)
        vemp_ifs = id_IFS_in.variables['flx_emp_sv'][:]
        ve_ifs   = id_IFS_in.variables['flx_e_sv'][:]
        vp_ifs   = id_IFS_in.variables['flx_p_sv'][:]
        vemp_glb_ifs = id_IFS_in.variables['flx_emp_glb_sv'][:]
        #ve_glb_ifs   = id_IFS_in.variables['flx_e_glb_sv'][:]
        #vp_glb_ifs   = id_IFS_in.variables['flx_p_glb_sv'][:]
        vemp_land_ifs = id_IFS_in.variables['flx_emp_land_sv'][:]
        ve_land_ifs   = id_IFS_in.variables['flx_e_land_sv'][:]
        vp_land_ifs   = id_IFS_in.variables['flx_p_land_sv'][:]
        id_IFS_in.close()
        if len(vemp_ifs) != nbm:
            print 'ERROR: '+csn+' => length of E-P of IFS in '+cf_IFS_in+' does not agree with its NEMO counterpart!'
            print '       =>', len(vemp_ifs), nbm
            sys.exit(0)
        l_fwf_ifs = True
    else:
        print '       => Nope!\n'
        
    # Annual data
    VY, FY = bt.monthly_2_annual(vtime, vfwf)
    # Time to plot
    bp.plot("1d_mon_ann")(vtime, VY, vfwf, FY, cfignm=cdiag+'_fwf_'+CONFEXP, dt=ittic,
                          cyunit=cyu, ctitle = CONFEXP+': '+clnm, ymin=ym, ymax=yp, cfig_type=ff)

    if l_rnf:
        VY, FY = bt.monthly_2_annual(vtime, vrnf)
        bp.plot("1d_mon_ann")(vtime, VY, vrnf, FY, cfignm=cdiag+'_rnf_'+CONFEXP, dt=ittic,
                              cyunit=cyu, ctitle = CONFEXP+': '+cln2, ymin=ym, ymax=yp, cfig_type=ff)

    if l_emp:
        VY, FY = bt.monthly_2_annual(vtime, vemp)
        bp.plot("1d_mon_ann")(vtime, VY, vemp, FY, cfignm=cdiag+'_emp_'+CONFEXP, dt=ittic,
                              cyunit=cyu, ctitle = CONFEXP+': '+cln3, ymin=ym, ymax=yp, cfig_type=ff)
    if l_evp:
        VY, FY = bt.monthly_2_annual(vtime, vevp)
        bp.plot("1d_mon_ann")(vtime, VY, vevp, FY, cfignm=cdiag+'_evp_'+CONFEXP, dt=ittic,
                              cyunit=cyu, ctitle = CONFEXP+': '+cln6, ymin=ym, ymax=yp, cfig_type=ff)
    if l_prc and l_prc_nemo_valid:
        VY, FY = bt.monthly_2_annual(vtime, vprc)
        bp.plot("1d_mon_ann")(vtime, VY, vprc, FY, cfignm=cdiag+'_prc_'+CONFEXP, dt=ittic,
                              cyunit=cyu, ctitle = CONFEXP+': '+cln4, ymin=ym, ymax=yp, cfig_type=ff)

    if l_evp and l_prc and l_prc_nemo_valid:
        VY, FY = bt.monthly_2_annual(vtime, vevp-vprc)
        bp.plot("1d_mon_ann")(vtime, VY, vevp-vprc, FY, cfignm=cdiag+'_prc_'+CONFEXP, dt=ittic,
                              cyunit=cyu, ctitle = CONFEXP+': E-P as E-P !', ymin=ym, ymax=yp, cfig_type=ff)


    if l_clv:
        VY, FY = bt.monthly_2_annual(vtime, vclv)
        bp.plot("1d_mon_ann")(vtime, VY, vclv, FY, cfignm=cdiag+'_clv_'+CONFEXP, dt=ittic,
                              cyunit=cyu, ctitle = CONFEXP+': '+cln5, ymin=ym, ymax=yp, cfig_type=ff)


    # Only runoffs (-(E-P) over land for IFS):
    if l_fwf_ifs and l_rnf:
        vlab = [] ; nbd = 2
        if l_clv: nbd = 3
        Xplt = nmp.zeros((nbd,nbm))
        Xplt[0,:] = vrnf[:]                     ; vlab.append('R NEMO')
        Xplt[1,:] = -vemp_land_ifs[:]           ; vlab.append('-(E-P) over land IFS')
        if l_clv: Xplt[2,:] = vrnf[:] + vclv[:] ; vlab.append('R + Ice Calving NEMO')
        bp.plot("1d_multi")(vtime, Xplt, vlab, cfignm=cdiag+'_rnf_NEMO_IFS_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': Continental runoffs (monthly)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out')
        # Same but annual:
        Xplt = nmp.zeros((nbd,nby))        
        VY, Xplt[0,:] = bt.monthly_2_annual(vtime[:], vrnf[:])
        VY, Xplt[1,:] = bt.monthly_2_annual(vtime[:], -vemp_land_ifs[:])
        if l_clv: VY, Xplt[2,:] = bt.monthly_2_annual(vtime[:], vrnf[:] + vclv[:])
        bp.plot("1d_multi")(VY, Xplt, vlab, cfignm=cdiag+'_rnf_NEMO_IFS_annual_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': Continental runoffs (annual)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out',
                            cinfo='Mean diff = '+str(round(nmp.mean(vrnf[:]+vemp_land_ifs[:]),3))+' '+cyu )


    # Only runoff and calving in NEMO:
    if l_clv and l_rnf:
        vlab = [] ; nbd = 2
        Xplt = nmp.zeros((nbd,nbm))
        cttl = 'NEMO: '+CONFEXP+': Continental Runoffs and Ice Calving'
        cfig = cdiag+'_rnf_clv_NEMO_'
        Xplt[0,:] = vrnf[:] ; vlab.append('R NEMO ('+vdic_fwf['NN_RNF']+')')
        Xplt[1,:] = vclv[:] ; vlab.append('Ice Calving NEMO ('+vdic_fwf['NN_CLV']+')')
        bp.plot("1d_multi")(vtime, Xplt, vlab, cfignm=cfig+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = cttl+' (monthly)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out')
        # Same but annual:
        Xplt = nmp.zeros((nbd,nby))        
        VY, Xplt[0,:] = bt.monthly_2_annual(vtime[:], vrnf[:])
        VY, Xplt[1,:] = bt.monthly_2_annual(vtime[:], vclv[:])
        bp.plot("1d_multi")(VY, Xplt, vlab, cfignm=cfig+'annual_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle =  cttl+' (annual)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out')



    # Only Precip (NEMO and IFS)
    if l_fwf_ifs and l_prc and l_prc_nemo_valid:
        vlab = [] ; nbd = 2
        Xplt = nmp.zeros((nbd,nbm))
        Xplt[0,:] = vprc[:]           ; vlab.append('P NEMO')
        Xplt[1,:] = vp_ifs[:]         ; vlab.append('P IFS')
        bp.plot("1d_multi")(vtime, Xplt, vlab, cfignm=cdiag+'_prc_NEMO_IFS_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': Precip (monthly)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out')
        # Same but annual:
        Xplt = nmp.zeros((nbd,nby))
        VY, Xplt[0,:] = bt.monthly_2_annual(vtime[:], vprc[:])
        VY, Xplt[1,:] = bt.monthly_2_annual(vtime[:], vp_ifs[:])
        bp.plot("1d_multi")(VY, Xplt, vlab, cfignm=cdiag+'_prc_NEMO_IFS_annual_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': Precip (annual)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out',
                            cinfo='Mean diff = '+str(round(nmp.mean(vprc[:]-vp_ifs[:]),3))+' '+cyu )


    # Only Evaporation (NEMO and IFS)
    if l_fwf_ifs and l_evp:
        vlab = [] ; nbd = 2
        if l_evb :  nbd = 3
        Xplt = nmp.zeros((nbd,nbm))
        Xplt[0,:] = vevp[:]           ; vlab.append('E NEMO ('+vdic_fwf['NN_E']+')')
        Xplt[1,:] = ve_ifs[:]         ; vlab.append('E IFS')
        if l_evb: Xplt[2,:] = vevb[:] ; vlab.append('E NEMO ('+cv_evb+')')
        bp.plot("1d_multi")(vtime, Xplt, vlab, cfignm=cdiag+'_evp_NEMO_IFS_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': Evaporation (monthly)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out')
        # Same but annual:
        Xplt = nmp.zeros((nbd,nby))
        VY, Xplt[0,:] =       bt.monthly_2_annual(vtime[:], vevp[:])
        VY, Xplt[1,:] =       bt.monthly_2_annual(vtime[:], ve_ifs[:])
        if l_evb: Xplt[2,:] = bt.monthly_2_annual(vtime[:], vevb[:])
        bp.plot("1d_multi")(VY, Xplt, vlab, cfignm=cdiag+'_evp_NEMO_IFS_annual_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': Evaporation (annual)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out',
                            cinfo='Mean diff = '+str(round(nmp.mean(vevp[:]-ve_ifs[:]),3))+' '+cyu )


    # Only [ Evaporation - Precipitation ] (NEMO and IFS)
    if l_fwf_ifs and l_evp and l_prc and l_prc_nemo_valid:
        vlab = [] ; nbd = 2
        Xplt = nmp.zeros((nbd,nbm))
        Xplt[0,:] = vevp[:]   - vprc[:]   ; vlab.append('E-P NEMO')
        Xplt[1,:] = ve_ifs[:] - vp_ifs[:] ; vlab.append('E-P IFS')
        bp.plot("1d_multi")(vtime, Xplt, vlab, cfignm=cdiag+'_EmP_NEMO_IFS_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': E-P (monthly)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out')
        # Same but annual:
        Xplt = nmp.zeros((nbd,nby))
        VY, Xplt[0,:] =       bt.monthly_2_annual(vtime[:], vevp[:]   - vprc[:])
        VY, Xplt[1,:] =       bt.monthly_2_annual(vtime[:], ve_ifs[:] - vp_ifs[:])
        bp.plot("1d_multi")(VY, Xplt, vlab, cfignm=cdiag+'_EmP_NEMO_IFS_annual_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': E-P (annual)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out',
                            cinfo='Mean diff = '+str(round(nmp.mean((vevp[:]-vprc[:])-(ve_ifs[:]-vp_ifs[:])),3))+' '+cyu )


    # Only [ Evaporation - Precipitation - Runoffs ] (NEMO and IFS)
    if l_fwf_ifs and l_evp and l_prc and l_prc_nemo_valid and l_rnf:
        vlab = [] ; nbd = 3
        if l_clv: nbd = 4
        Xplt = nmp.zeros((nbd,nbm))
        Xplt[0,:] = vevp[:]   - vprc[:]   - vrnf[:]           ; vlab.append('E-P-R NEMO (as E-P-R)')
        Xplt[1,:] = ve_ifs[:] - vp_ifs[:] + vemp_land_ifs[:] ; vlab.append('E-P-R IFS')
        Xplt[2,:] = vfwf[:]          ; vlab.append('NEMO: '+vdic_fwf['NN_FWF'])
        if l_clv: Xplt[3,:] = vfwf[:] + vclv[:] ; vlab.append('NEMO: '+vdic_fwf['NN_FWF']+'+'+vdic_fwf['NN_CLV'])
        bp.plot("1d_multi")(vtime, Xplt, vlab, cfignm=cdiag+'_EmPmR_NEMO_IFS_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': E-P-R (monthly)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out')
        # Same but annual:
        Xplt = nmp.zeros((nbd,nby))
        VY, Xplt[0,:] = bt.monthly_2_annual(vtime[:], vevp[:]   - vprc[:]   - vrnf[:])
        VY, Xplt[1,:] = bt.monthly_2_annual(vtime[:], ve_ifs[:] - vp_ifs[:] + vemp_land_ifs[:])
        VY, Xplt[2,:] = bt.monthly_2_annual(vtime[:], vfwf[:])
        if l_clv: Vy, Xplt[3,:] = bt.monthly_2_annual(vtime[:], vfwf[:] + vclv[:])
        bp.plot("1d_multi")(VY, Xplt, vlab, cfignm=cdiag+'_EmPmR_NEMO_IFS_annual_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = 'NEMO & IFS, '+CONFEXP+': E-P-R (annual)',
                            ymin=ym, ymax=yp, cfig_type=ff, loc_legend='out',
                            cinfo='Mean diff = '+str(round(nmp.mean((vevp[:]-vprc[:]-vrnf[:])-(ve_ifs[:]-vp_ifs[:]+vemp_land_ifs[:])),3))+' '+cyu )




    # Only P for NEMO and IFS, and RNF NEMO:
    if l_fwf_ifs and l_prc:
        vlab = [] ; nbd = 3
        if l_rnf: nbd = 4
        if l_rnf and l_clv: nbd = 5
        Xplt = nmp.zeros((nbd,nbm))
        if not l_prc_nemo_valid:
            print 'WARNING: NEMO precip is NOTHING!!! Filling with 0! ('+csn+')'
            Xplt[0,:] = 0.0        ; vlab.append('P NEMO: MISSING in NEMO output file!')
        else:
            Xplt[0,:] = vprc[:]    ; vlab.append('P NEMO')
        Xplt[1,:] = vp_ifs[:]      ; vlab.append('P IFS (oceans)')
        Xplt[2,:] = vp_land_ifs[:] ; vlab.append('P IFS (land)')
        if l_rnf:
            Xplt[3,:] = vrnf[:]    ; vlab.append('R NEMO')
        if l_rnf and l_clv:
            Xplt[4,:] = vclv[:]    ; vlab.append('Calving NEMO')
        bp.plot("1d_multi")(vtime, Xplt, vlab, cfignm=cdiag+'_prc_IFS_'+CONFEXP, dt=ittic,
                            cyunit=cyu, ctitle = CONFEXP+': Precip and NEMO runoffs (monthly)', ymin=ym, ymax=yp, cfig_type=ff,
                            loc_legend='out')




##########################################
# AMOC
##########################################

if idfig == 'amoc':
    clmoc = vdic['LMOCLAT']
    list_lat = clmoc.split() ; nblat = len(list_lat)
    print '\n AMOC: '+str(nblat)+' latitude bands!'

    i40 = 2 ; # position of AMOC at 40!

    jl = 0
    for clr in list_lat:
        [ c1, c2 ] = clr.split('-') ; clat_info = '+'+c1+'N+'+c2+'N'
        cf_in = 'max_moc_atl_'+clat_info+'.nc' ; bt.chck4f(cf_in, script_name=csn)
        id_in = Dataset(cf_in)
        if jl==0:
            vtime = id_in.variables['time'][:]
            (nby, nbm, nbr, ittic) = bt.test_nb_years(vtime, cdiag)
            vlabels = nmp.zeros(nblat, dtype = nmp.dtype('a8'))
            Xamoc   = nmp.zeros((nblat , nbr))
        vlabels[jl] = clat_info
        Xamoc[jl,:] = id_in.variables['moc_atl'][:]
        id_in.close()
        
        jl = jl + 1


    # Plot annual+montly for AMOC at 40
    VY = nmp.zeros(nby)
    FY = nmp.zeros(nby)
    if nbm >= 12:
        VY[:], FY[:] = bt.monthly_2_annual(vtime, Xamoc[i40,:])
    else:
        # the file contains annual data
        VY[:] = vtime[:]
        FY[:] = Xamoc[i40,:]

    # Time to plot
    bp.plot("1d_mon_ann")(vtime, VY, Xamoc[i40,:], FY, cfignm=cdiag+'_'+CONFEXP, dt=ittic,
                          cyunit=cyu, ctitle = CONFEXP+': '+r'Max. of AMOC between '+vlabels[i40],
                          ymin=ym, ymax=yp, dy=1., i_y_jump=2, cfig_type=ff, y_cst_to_add=10.)


    # Plot annual for AMOC at specified latitudes:
    FY = nmp.zeros((nblat , nby))
    if nbm >= 12:
        # the file contains monthly data (nbm=-1 otherwize)            
        VY[:], FY[:,:]  = bt.monthly_2_annual(vtime, Xamoc[:,:])
    else:
        # the file contains annual data
        FY[:,:] = Xamoc[:,:]

    bp.plot("1d_multi")(VY, FY, vlabels, cfignm=cdiag+'_'+CONFEXP+'_comp', dt=ittic,
                        cyunit=cyu, ctitle = CONFEXP+': '+r'Max. of AMOC', ymin=0, ymax=0,
                        loc_legend='out', cfig_type=ff)





if idfig == 'ice':

    vlab_sum = [ 'Arctic (Sept.)'   , 'Antarctic (March)' ]
    vlab_win = [ 'Arctic (March)'   , 'Antarctic (Sept.)' ]

    # montly sea-ice volume and area, Arctic and Antarctic...
    cf_in = 'seaice_diags.nc' ;  bt.chck4f(cf_in, script_name=csn)
    id_in = Dataset(cf_in)
    vtime = id_in.variables['time'][:]
    vvolu_n  = id_in.variables['volu_ne'][:]
    varea_n  = id_in.variables['area_ne'][:]
    vvolu_s  = id_in.variables['volu_se'][:]
    varea_s  = id_in.variables['area_se'][:]
    id_in.close()

    (nby, nbm, nbr, ittic) = bt.test_nb_years(vtime, cdiag)

    cyua = r'10$^6$km$^2$'
    cyuv = r'10$^3$km$^3$'

    vtime_y = nmp.zeros(nby)
    Xplt = nmp.zeros((2 , nby))

    vtime_y, FY = bt.monthly_2_annual(vtime[:], vvolu_n[:])

    # End local summer
    Xplt[0,:] = varea_n[8::12] ; # area Arctic september
    Xplt[1,:] = varea_s[2::12] ; # area Antarctic march
    bp.plot("1d_multi")(vtime_y, Xplt, vlab_sum, cfignm='seaice_area_summer_'+CONFEXP, dt=ittic,
                        cyunit=cyua, ctitle = CONFEXP+': '+r'Sea-ice area, end of local summer',
                        loc_legend='out', ymin=0., ymax=0., cfig_type=ff)

    Xplt[0,:] = vvolu_n[8::12] ; # volume Arctic september
    Xplt[1,:] = vvolu_s[2::12] ; # volume Antarctic march
    bp.plot("1d_multi")(vtime_y, Xplt, vlab_sum, cfignm='seaice_volume_summer_'+CONFEXP, dt=ittic,
                        cyunit=cyuv, ctitle = CONFEXP+': '+r'Sea-ice volume, end of local summer',
                        loc_legend='out', ymin=0., ymax=0., cfig_type=ff)

    # End of local winter
    Xplt[0,:] = varea_n[2::12] ; # area Arctic march
    Xplt[1,:] = varea_s[8::12] ; # area Antarctic september
    bp.plot("1d_multi")(vtime_y, Xplt, vlab_win, cfignm='seaice_area_winter_'+CONFEXP, dt=ittic,
                        cyunit=cyua, ctitle = CONFEXP+': '+r'Sea-ice area, end of local winter',
                        loc_legend='out', ymin=0., ymax=0., cfig_type=ff)

    Xplt[0,:] = vvolu_n[2::12] ; # volume Arctic march
    Xplt[1,:] = vvolu_s[8::12] ; # volume Antarctic september
    bp.plot("1d_multi")(vtime_y, Xplt, vlab_win, cfignm='seaice_volume_winter_'+CONFEXP, dt=ittic,
                        cyunit=cyuv, ctitle = CONFEXP+': '+r'Sea-ice volume, end of local winter',
                        loc_legend='out', ymin=0., ymax=0., cfig_type=ff)




if idfig == 'transport':
    js = 0
    for csec in list_sections:

        print '\n * treating section '+csec

        cf_in = 'transport_sect_'+csec+'.nc' ;   bt.chck4f(cf_in, script_name=csn)                

        nbtrsp = 4
        
        # Checking if the same section was done for sea-ice transport:
        cf_ice = 'transport_ice_sect_'+csec+'.nc'
        l_add_ice = os.path.exists(cf_ice)
        if l_add_ice: nbtrsp = nbtrsp+1

        # Reading ocean transports:
        id_in = Dataset(cf_in)
        if js == 0:
            vtime = id_in.variables['time'][:]
            (nby, nbm, nbr, ittic) = bt.test_nb_years(vtime, cdiag)
        Xtrsp   = nmp.zeros((nbtrsp , nbr)) ; # time + nbtrsp types of transport
        Xtrsp[0,:] = id_in.variables['trsp_volu'][:]
        Xtrsp[1,:] = id_in.variables['trsp_heat'][:]
        Xtrsp[2,:] = id_in.variables['trsp_salt'][:]
        Xtrsp[3,:] = id_in.variables['trsp_frwt'][:]
        cref_temp  = id_in.variables['trsp_heat'].Tref
        cref_sali  = id_in.variables['trsp_salt'].Sref
        id_in.close()

        # Reading ice transport:
        if l_add_ice:
            id_ice = Dataset(cf_ice)
            vtmp = id_ice.variables['trsp_frwt'][:]
            if len(vtmp) != nbr:
                print 'ERROR: '+csn+' => length of trsp_frwt in '+cf_ice+' doesnot match with that in '+cf_in+'!'
                sys.exit(0)
            Xtrsp[4,:] = vtmp[:]
            id_ice.close()
            del vtmp
    

        VY = nmp.zeros(nby)
        FY = nmp.zeros((nbtrsp , nby))
        if nbm >= 12:
            VY[:], FY[:,:] = bt.monthly_2_annual(vtime, Xtrsp[:,:])
        else:
            # the file contains annual data
            VY[:]   = vtime[:]
            FY[:,:] = Xtrsp[:,:]

        # Transport of volume:
        bp.plot("1d_mon_ann")(vtime, VY, Xtrsp[0,:], FY[0,:], cfignm='transport_vol_'+csec+'_'+CONFEXP,
                              dt=ittic, cyunit='Sv', ctitle = CONFEXP+': transport of volume, '+csec,
                              ymin=0, ymax=0, cfig_type=ff, y_cst_to_add=0.)

        # Transport of heat:
        bp.plot("1d_mon_ann")(vtime, VY, Xtrsp[1,:], FY[1,:], cfignm='transport_heat_'+csec+'_'+CONFEXP,
                              dt=ittic, cyunit='PW', ctitle = CONFEXP+': transport of heat (Tref='+cref_temp+'C), '+csec,
                              ymin=0, ymax=0, mnth_col='g', cfig_type=ff, y_cst_to_add=0.)

        # Transport of freshwater:
        if l_add_ice:
            # Transport of liquid + solid freshwater:
            bp.plot("1d_multi")(VY, nmp.array([FY[3,:],FY[3,:]+FY[4,:]]), ['liquid', 'liquid+solid'], cfignm='transport_lsfw_'+csec+'_'+CONFEXP,
                                dt=ittic, loc_legend='out', cyunit='Sv', ctitle = CONFEXP+': transport of freshwater (Sref='+cref_sali+'), '+csec,
                                ymin=0, ymax=0, cfig_type=ff, y_cst_to_add=0.)
            bp.plot("1d_mon_ann")(vtime, VY, Xtrsp[3,:]+Xtrsp[4,:], FY[3,:]+FY[4,:], cfignm='transport_fw_'+csec+'_'+CONFEXP,
                                  dt=ittic, cyunit='Sv', ctitle = CONFEXP+': transport of (liquid+solid) freshwater (Sref='+cref_sali+'), '+csec,
                                  ymin=0, ymax=0, mnth_col='#738FBF', cfig_type=ff, y_cst_to_add=0.)
        else:
            # Transport of liquid freshwater only:
            bp.plot("1d_mon_ann")(vtime, VY, Xtrsp[3,:], FY[3,:], cfignm='transport_fw_'+csec+'_'+CONFEXP,
                                  dt=ittic, cyunit='Sv', ctitle = CONFEXP+': transport of (liquid) freshwater (Sref='+cref_sali+'), '+csec,
                                  ymin=0, ymax=0, mnth_col='#738FBF', cfig_type=ff, y_cst_to_add=0.)



        
        js = js + 1


#################################################
# MLD in regions defined in the basin_mask file!
#################################################
if idfig == 'mld':

    list_basin_names, list_basin_lgnms = bo.get_basin_info(vdic['BM_FILE'])    
    nb_oce = len(list_basin_names)
    joce = 0
    for coce in list_basin_names[:]:
        cf_in_m = 'mean_'+cvar+'_'+CONFEXP+'_'+coce+'.nc'
        if os.path.exists(cf_in_m):
            print ' Opening '+cf_in_m
            vt0, vd0 = bn.read_1d_series(cf_in_m, cvar, cv_t='time', l_return_time=True)
            if joce==0: (nby, nbm, nbr, ittic) = bt.test_nb_years(vt0, cdiag)
            VY, FY = bt.monthly_2_annual(vt0, vd0)

            bp.plot("1d_mon_ann")(vt0, VY, vd0, FY, cfignm=cdiag+'_'+CONFEXP+'_'+coce, dt=ittic,
                                  cyunit=cyu, ctitle = CONFEXP+': '+clnm+list_basin_lgnms[joce],
                                  ymin=ym, ymax=yp,
                                  plt_m03=True, plt_m09=True, cfig_type=ff)
        else:
            print 'WARNING: '+csn+' => MLD diag => '+cf_in_m+' not found!'
        joce = joce+1


print ''+csn+' done...\n'






