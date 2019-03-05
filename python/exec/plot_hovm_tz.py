#!/usr/bin/env python

#       B a r a K u d a
#
#     Generate time-depth Hovmoeller diagrams of 3D fields out of NEMO output files...
#
#      L. Brodeau, 2011
#

import sys
import os
import numpy as nmp

from netCDF4 import Dataset

import barakuda_tool as bt
import barakuda_orca as bo
import barakuda_plot as bp


venv_needed = {'ORCA','EXP','DIAG_D','NN_T','NN_S','BM_FILE'}

vdic = bt.check_env_var(sys.argv[0], venv_needed)

CONFEXP = vdic['ORCA']+'-'+vdic['EXP']

cname_temp = vdic['NN_T']
cname_sali = vdic['NN_S']



#if len(sys.argv) != 4 and len(sys.argv) != 6 :
#    print 'Usage: '+sys.argv[0]+' <YYYY1> <YYYY2> <Nb. Levels> (<name temp.> <name salin.>)'
#    sys.exit(0)

#cy1 = sys.argv[1] ; cy2 = sys.argv[2] ; jy1=int(cy1); jy2=int(cy2)



path_fig=vdic['DIAG_D']+'/'

fig_type='png'


list_basin_names, list_basin_lgnms = bo.get_basin_info(vdic['BM_FILE'])

#list_basin_names_U = [cc.upper() for cc in list_basin_names]  ; # same list but in uppercase


jo = 0
for coce in list_basin_names:

    cf_temp = cname_temp+'_mean_Vprofile_'+CONFEXP+'_'+coce+'.nc' ; bt.chck4f(cf_temp)
    cf_sali = cname_sali+'_mean_Vprofile_'+CONFEXP+'_'+coce+'.nc' ; bt.chck4f(cf_sali)

    id_temp = Dataset(cf_temp)
    if jo == 0:
        vyears = id_temp.variables['time'][:]
        vdepth = id_temp.variables['deptht'][:]
    XT = id_temp.variables[cname_temp][:,:]
    id_temp.close()

    id_sali = Dataset(cf_sali)
    XS = id_sali.variables[cname_sali][:,:]
    id_sali.close()


    if jo == 0:
        vyears = nmp.trunc(vyears) + 0.5 ; # in case 1990 and not 1990.5 !!!
        yr1=float(int(min(vyears)))
        yr2=float(int(max(vyears)))


    [nby, nz] = XT.shape

    ixtics = bt.iaxe_tick(nby)

    # Number of NaN vertical points:
    visnan = nmp.isnan(XT[0,:])
    nz_nan = nmp.sum(visnan)
    nz = nz - nz_nan

    XTe = nmp.zeros((nz,nby))
    XTe[:,:] = nmp.flipud(nmp.rot90(XT[:,:nz]))

    XSe = nmp.zeros((nz,nby))
    XSe[:,:] = nmp.flipud(nmp.rot90(XS[:,:nz]))



    # Removing value for first year to all years:
    vy1 = nmp.zeros(nz) ; vy1[:] = XTe[:,0]
    for jy in range(nby): XTe[:,jy] = XTe[:,jy] - vy1[:]
    vy1 = nmp.zeros(nz) ; vy1[:] = XSe[:,0]
    for jy in range(nby): XSe[:,jy] = XSe[:,jy] - vy1[:]

    z0 = vdepth[0]
    zK = max(vdepth)

    [ rmin, rmax, rdf ] = bt.get_min_max_df(XTe,40)
    bp.plot("hovmoeller")(vyears[:], vdepth[:nz], XTe[:,:], XTe[:,:]*0.+1., rmin, rmax, rdf, c_y_is='depth', # 
                          cpal='RdBu_r', tmin=yr1, tmax=yr2+1., dt=ixtics, lkcont=True,
                          ymin = z0, ymax = zK, l_ylog=True,
                          cfignm=path_fig+'hov_temperature_'+CONFEXP+'_'+coce, cbunit=r'$^{\circ}$C', ctunit='',
                          cyunit='Depth (m)',
                          ctitle=CONFEXP+': Temperature evolution, '+list_basin_lgnms[jo]+', ('+str(int(yr1))+'-'+str(int(yr2))+')',
                          cfig_type=fig_type, i_cb_subsamp=2)

    XSe = 1000.*XSe
    [ rmin, rmax, rdf ] = bt.get_min_max_df(XSe,40)
    bp.plot("hovmoeller")(vyears[:], vdepth[:nz], XSe[:,:], XSe[:,:]*0.+1., rmin, rmax, rdf, c_y_is='depth',
                          cpal='PiYG_r', tmin=yr1, tmax=yr2+1., dt=ixtics, lkcont=True,
                          ymin = z0, ymax = zK, l_ylog=True,
                          cfignm=path_fig+'hov_salinity_'+CONFEXP+'_'+coce, cbunit=r'10$^{-3}$PSU', ctunit='',
                          cyunit='Depth (m)',
                          ctitle=CONFEXP+': Salinity evolution, '+list_basin_lgnms[jo]+', ('+str(int(yr1))+'-'+str(int(yr2))+')',
                          cfig_type=fig_type, i_cb_subsamp=2)


    jo = jo +1
