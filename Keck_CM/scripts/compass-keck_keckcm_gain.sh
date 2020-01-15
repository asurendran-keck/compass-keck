#!/bin/bash
script_name="compass-keck_keckcm_ngs_circ.py"
param_name="scao_sh_20x20_4pix_keck_ngs_ml_tt.py"
result_name="${param_name::-3}.txt"
m='10'
#r0=('0.16'
#gain=($(seq 0.05 0.05 0.8))
gain='0.2'
#'0.1567' '0.1468' '0.13' '0.1056')
#z=('0')
niter=('10000')
# '15' '30' '45' '60') # only used for altitude compensation
path_script="/home/aodev/asurendran/scripts/test_scripts/main"
path_params="/home/aodev/asurendran/param/1_recon"
path_result="/home/aodev/asurendran/Results/1_recon"
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
python h5panda.py
for j in "${!gain[@]}"
  do
    CMD="python $script $param --save_filename "$savepath" --gain ${gain[$j]} --niter $niter"
    echo "execute $CMD" >> $output
    $CMD #2>> $output >> $output
  done
