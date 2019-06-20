#!/bin/bash

###############################################################################
#                   BARAKUDA a1om EXPERIMENT
###############################################################################
#
#SBATCH --qos=serial
#SBATCH -A Earth
#
#
#
#SBATCH -n 6
#SBATCH -t 05:00:00
#SBATCH -J a1om_BARAKUDA
#SBATCH -o /home/Earth/tarsouze/Documents/barakuda/a1om_BARAKUDA.%J.out
#SBATCH -e /home/Earth/tarsouze/Documents/barakuda/a1om_BARAKUDA.%J.err
#SBATCH --nodes=1-1
#
###############################################################################
###################
# Autosubmit header
###################
set -xuve

###################
# Autosubmit job
###################

#!/bin/bash

set -xuve

#Autosubmit variables from proj.conf
export EXPID=a1om
HPCARCH=moore
ORCA_CONF=ORCA1L75
ORCA_CONF=${ORCA_CONF/L/_L}
INSTITUTION=EC-Earth-Consortium
export MIP=OMIP
export MODEL_ID=EC-Earth3-LR
export MEMBER=r2i1p1f1
export EXPERIMENT=piControl
export GRID_TYPE=gn
export CONFIG_FILE=config_${ORCA_CONF}_${EXPID}.sh
export ORCA_CONF=${ORCA_CONF/_/.} #format needed for the barakuda config file
export DATELIST=18610101
export RES=`echo $ORCA_CONF | cut -d'.' -f1`

#Paths
barakudadir=/home/Earth/tarsouze/Documents/barakuda
datadir=/esarchive/exp/ecearth/${EXPID}/monthly_means #This path requires the relink
outdir=/esarchive/exp/ecearth/${EXPID}/barakuda #In case we save the bk diags in the exp folder

case ${HPCARCH} in
   moore) export CDFTOOLS_ROOT=/esarchive/scratch/barakuda/cdftools_light/Gustafson ;;
   hpc9)  export CDFTOOLS_ROOT=/esarchive/scratch/barakuda/cdftools_light/Power9 ;;
esac

cd ${barakudadir}

#Output dir 
if [ ! -d ${outdir} ] ; then
  echo ${outdir} not present, creating it
  mkdir -p ${outdir}
  mkdir -p ${outdir}/log
fi

cd configs
barakudadiresc=$(echo ${barakudadir} | sed 's_/_\\/_g')
sed -e "s/_ORCA_CONF_/${ORCA_CONF}/" \
    -e "s/_EXPID_/${EXPID}/" \
    -e "s/_RES_/${RES}/" \
    -e "s/_MIP_/${MIP}/" \
    -e "s/_INSTITUTION_/${INSTITUTION}/" \
    -e "s/_EXPERIMENT_/${EXPERIMENT}/" \
    -e "s/_MODEL_ID_/${MODEL_ID}/" \
    -e "s/_MEMBER_/${MEMBER}/" \
    -e "s/_barakudadir_/${barakudadiresc}/" config_BSC_barakuda.sh > ${CONFIG_FILE}

cp ${CONFIG_FILE} ${outdir}/log/
cd ..

#Load necessary modules, add python? python/2.7.12-01
set +xuve
LIST_MOD="netCDF-Fortran/4.2-foss-2015a NCO"
module add ${LIST_MOD}
set -xuve

#export OMP_NUM_THREADS=$EC_threads_per_task

#--------------
#Launch barakuda (launch both jobs automatically)
#First calculate diags
CONFIG=`echo ${CONFIG_FILE} | cut -d '_' -f2- | cut -d '.' -f-1`
${barakudadir}/barakuda.sh -C ${CONFIG} -R ${EXPID} 
#---------------

#Now do the plots
${barakudadir}/barakuda.sh -C ${CONFIG} -R ${EXPID} -F -e
set +xuve
module rm ${LIST_MOD}
set -xuve

#Transfer to website

###################
# Autosubmit tailer
###################
set -xuve
echo $(date +%s) >> ${job_name_ptrn}_STAT
touch ${job_name_ptrn}_COMPLETED
exit 0

