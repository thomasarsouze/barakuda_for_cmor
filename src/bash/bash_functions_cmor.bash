#!/usr/bin/env bash

##TA here

function barakuda_first_last_years()
{
    cd ${NEMO_OUT_D}/
    if [ ${CMOR} -eq 1 ]; then
        cd Omon/
        if [ ! -d ${NN_T} ]; then
            echo " *** Inside: `pwd` !"; \ls -l ; echo
            echo "ERROR: since CMOR=${CMOR}, there should be at least a directory ${NN_T} in:"; echo " ${NEMO_OUT_D}"; echo; exit
        fi
        cd ${NN_T}/${GRID_TYPE}/v????????/
        nby_ece=`\ls ${NN_T}*.nc |  wc -l`
        echo " ${nby_ece} years have been completed..."
    fi

    # Try to guess the first year from files:
    YEAR_INI=`\ls ${NN_T}*.nc | head -1 | cut -d. -f1 | tail -c 7 | cut -c1-4`
    echo ${YEAR_INI} |  grep "[^0-9]" >/dev/null ;   # Checking if it's an integer:
    if [ ! "$?" -eq 1 ]; then
        echo "ERROR: it was imposible to guess initial year from your input files"
        echo "       maybe the directory contains non-related files..."
        exit
    fi
    export YEAR_INI_F=${YEAR_INI} ; # saving the year deduced from first file

    if ${LFORCE_YINI}; then
        if [ ${YEAR0} -lt ${YEAR_INI_F} ]; then echo "ERROR: forced initial year is before first year!"; exit; fi
        export YEAR_INI=${YEAR0}
        echo " Initial year forced to ${YEAR_INI} !"
    fi

    if [ ${CMOR} -eq 1 ]; then
        file_base=`\ls ${NN_T}*.nc | head -1 | head -c -17` ## TA : this "17" should be ok as CMOR leads to standard names
        export YEAR_END=$((${YEAR_INI_F}+${nby_ece}-1))
        file_end=${file_base}${YEAR_END}01-${YEAR_END}12.nc
        if [ ! -f ${file_end} ]; then echo "ERROR: since CMOR=${CMOR}, and there are ${nby_ece} files found, there should be a file ${file_end} in:"; echo " ${NEMO_OUT_D}/${NN_T}/"; exit ; fi
    fi
    export YEAR_END_F=${YEAR_END} ; # saving the last year deduced from number of files

    if ${LFORCE_YEND}; then
        if [ ${YEARN} -gt ${YEAR_END_F} ]; then echo "ERROR: forced final year is after last year!"; exit; fi
        export YEAR_END=${YEARN}
        echo " Last year forced to ${YEAR_END} !"
    fi

    echo
    echo " *** Initial year set to ${YEAR_INI}"
    echo " ***   Last  year set to ${YEAR_END}"
    echo
}

function barakuda_import_files()
{
    # CMOR !!!
    echo
    echo "Inside barakuda_import_files => year = ${cyear}"
    export NEMO_OUT_D=`echo ${NEMO_OUT_STRCT} | sed -e "s|<EXP>|${EXP}|g"`
    cd ${NEMO_OUT_D}/

    cycm=`printf "%04d" $((${jyear}-1))`
    cycp=`printf "%04d" $((${jyear}+1))`

    echo " *** Going to extract year ${cyear} into:"
    echo "   ${TMP_DIR}"

    # suppose 1 file per year with monthly values, starting in january
    echo; echo " *** Going to ncks !!!***"; echo
    cd ${TMP_DIR}/
    for gt in ${NEMO_SAVED_FILES}; do
        ftt="./${CRT1M}_${gt}.nc" ;  rm -f ${ftt}
    done
    for var in ${NN_SST} ${NN_SSS} ${NN_SSH} ${NN_T} ${NN_S} ${NN_MLD}; do
       if ! [[ "${var}" =~ ^(0|X)$ ]] ; then   
          file=`ls ${NEMO_OUT_D}/Omon/${var}/${GRID_TYPE}/v????????/${var}_Omon_${MODEL_ID}_${EXPERIMENT}_${MEMBER}_${GRID_TYPE}_${cyear}01-${cyear}12.nc`
          echo "Putting var ${var} from file ${file} in file ${CRT1M}_grid_T.nc"
          ncks -A -3 -v ${var} ${file} ${CRT1M}_grid_T.nc
       fi
    done
    for var in ${NN_U} ${NN_TAUX} ${NN_U_EIV}; do
       if ! [[ "${var}" =~ ^(0|X)$ ]] ; then 
         file=`ls ${NEMO_OUT_D}/Omon/${var}/${GRID_TYPE}/v????????/${var}_Omon_${MODEL_ID}_${EXPERIMENT}_${MEMBER}_${GRID_TYPE}_${cyear}01-${cyear}12.nc`
          echo "Putting var ${var} from file ${file} in file ${CRT1M}_grid_U.nc"
          ncks -A -3 -v ${var} ${file} ${CRT1M}_grid_U.nc
       fi
    done
    for var in ${NN_V} ${NN_TAUY} ${NN_V_EIV}; do
       if ! [[ "${var}" =~ ^(0|X)$ ]] ; then   
         file=`ls ${NEMO_OUT_D}/Omon/${var}/${GRID_TYPE}/v????????/${var}_Omon_${MODEL_ID}_${EXPERIMENT}_${MEMBER}_${GRID_TYPE}_${cyear}01-${cyear}12.nc`
          echo "Putting var ${var} from file ${file} in file ${CRT1M}_grid_V.nc"
          ncks -A -3 -v ${var} ${file} ${CRT1M}_grid_V.nc
       fi
    done
    for var in ${NN_ICEF} ${NN_ICET} ${NN_ICEU} ${NN_ICEV}; do
       if ! [[ "${var}" =~ ^(0|X)$ ]] ; then   
         file=`ls ${NEMO_OUT_D}/SImon/${var}/${GRID_TYPE}/v????????/${var}_SImon_${MODEL_ID}_${EXPERIMENT}_${MEMBER}_${GRID_TYPE}_${cyear}01-${cyear}12.nc`
          echo "Putting var ${var} from file ${file} in file ${CRT1M}_${FILE_ICE_SUFFIX}.nc"
          ncks -A -3 -v ${var} ${file} ${CRT1M}_${FILE_ICE_SUFFIX}.nc
       fi
    done
    for var in ${NN_FWF} ${NN_EMP} ${NN_P} ${NN_RNF} ${NN_CLV} ${NN_E} ${NN_QNET} ${NN_QSOL} ${NN_TAUM} ${NN_WNDM}; do
       if ! [[ "${var}" =~ ^(0|X)$ ]] ; then   
         file=`ls ${NEMO_OUT_D}/Omon/${var}/${GRID_TYPE}/v????????/${var}_Omon_${MODEL_ID}_${EXPERIMENT}_${MEMBER}_${GRID_TYPE}_${cyear}01-${cyear}12.nc`
          echo "Putting var ${var} from file ${file} in file ${CRT1M}_${FILE_FLX_SUFFIX}.nc"
          ncks -A -3 -v ${var} ${file} ${CRT1M}_${FILE_FLX_SUFFIX}.nc
       fi
    done

    # Testing if ALL required files are present now:
    for gt in ${NEMO_SAVED_FILES}; do
        ftt="./${CRT1M}_${gt}.nc"
        ncrename -d i,x -d j,y -d time,time_counter -v time,time_counter -v longitude,nav_lon -v latitude,nav_lat ${ftt}
        if [[ ${gt} == "grid_T" ]] ; then
          ncrename -d lev,deptht -v lev,deptht ${ftt}
        elif [[ ${gt} == "grid_U" ]] ; then
          ncrename -d lev,depthu -v lev,depthu ${ftt}
        elif [[ ${gt} == "grid_V" ]] ; then
          ncrename -d lev,depthv -v lev,depthv ${ftt}
        elif [[ ${gt} == "icemod" ]] ; then
          ncrename -d x,x_grid_T -d y,y_grid_T ${ftt}
        fi
        check_if_file ${ftt}
    done
    echo; echo "All required files are in `pwd` for year ${cyear} !"; echo
}

function barakuda_check_year_is_complete()
{
    # CMOR !!!
    if ${lcontinue}; then
        if [ `ls ${NEMO_OUT_D}/Omon/${NN_SST}/${GRID_TYPE}/v????????/${NN_SST}_Omon_${MODEL_ID}_${EXPERIMENT}_${MEMBER}_${GRID_TYPE}_${cyear}01-${cyear}12.nc | wc -l` -eq 0 ]; then
            echo
            echo "Year ${cyear} is not here:"; echo " => ${cftar} is missing"; echo
            echo
            export lcontinue=false
        fi
    fi
    echo
}


