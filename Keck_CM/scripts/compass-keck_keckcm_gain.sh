#!/bin/bash
# This is the top level bash script which runs the compass-keck python script for the Keck CM pertaining to NGS mode
# and can be used to benchmark the performance with parameters like zenith angle, magnitude and gain.
# The example given here simulates the NGS mode with the Keck NGS parameter file and the Keck CM python script
# It runs the python script for a sequence of different gains to measure the AO performance output

# Setting the parameter file, python script file and result file names and paths
script_name="compass-keck_keckcm_ngs_circ.py"
param_name="scao_sh_20x20_4pix_keck_ngs_ml_tt.py"
result_name="${param_name::-3}.txt"
path_script="/home/aodev/asurendran/scripts/test_scripts/main"
path_params="/home/aodev/asurendran/param/1_recon"
path_result="/home/aodev/asurendran/Results/1_recon"
# Setting the gain array over which each python script will be run and number of AO loop iterations for every run
m='10'
gain=($(seq 0.05 0.05 0.8))
niter=('10000')

# Parsing filename for parameter, python script and result files
script="$path_script/$script_name"
param="$path_params/$param_name"
output="$path_script/${param_name::-3}.log"
savepath[$i]="$path_result/$result_name"
for i in "${!m[@]}"
do
savepath[$i]="$path_result/sr_vs_za_exp10_m${m[$i]}vs_gain.txt"
    if [ -f "${savepath[$i]}" ]; then
       echo "${savepath[$i]} exists, deleting the file"
       rm ${savepath[$i]}
    fi
done

if [ -f "$output" ]; then
    echo "Log file exists, deleting the file"
    rm $output
fi
# Running the custom DM HDF5 script
python h5panda.py
# Iteration of the python script over all the gains
for j in "${!gain[@]}"
  do
    CMD="python $script $param --save_filename "$savepath" --gain ${gain[$j]} --niter $niter"
    echo "execute $CMD" >> $output
    $CMD #2>> $output >> $output
  done
