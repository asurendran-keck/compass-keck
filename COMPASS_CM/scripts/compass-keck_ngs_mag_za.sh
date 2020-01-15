#!/bin/bash
## @package   compass-keck
## @brief     Top level bash script to obtain NGS AO performance with magnitude and ZA
## @author    Avinash Surendran
## @date      01/14/2020
# This is the top level bash script which runs the compass-keck python script pertaining to the NGS mode to test noise performance
# and can be used to benchmark the performance with zenith angle and magnitude.
# The example given here simulates the NGS mode with the Keck NGS parameter file, and runs the COMPASS simulation
# for five different zenith angle inputs and four different guidestar magnitudes
script_name="compass-keck_ngs.py"
param_name="scao_sh_20x20_4pix_keck_ngs_ml_dtt.py"
z=('0' '15' '30' '45' '60')
m=('6' '8' '10' '12')
path_script="/home/aodev/asurendran/scripts/benchmark"
path_params="/home/aodev/asurendran/param/benchmark"
path_result="/home/aodev/asurendran/Results/benchmark"
script="$path_script/$script_name"
param="$path_params/$param_name"
output="$path_script/${param_name::-3}.log"
for j in "${!m[@]}"
do
  result_name="${param_name::-3}_m${m[j]}.txt"
  savepath[$j]="$path_result/${result_name}"
done
if [ -f "${savepath[$i]}" ]; then
   echo "${savepath[$i]} exists, deleting the file"
   rm ${savepath[$i]}
fi
if [ -f "$output" ]; then
    echo "Log file exists, deleting the file"
    rm $output
fi
for i in "${!m[@]}"
do
  for j in "${!z[@]}"
  do
    CMD="python $script $param --save_filename "${savepath[$i]}" --zenith ${z[$j]} --magnitude ${m[$i]}"
    echo "execute $CMD" >> $output
    $CMD #2>> $output >> $output
  done
done
