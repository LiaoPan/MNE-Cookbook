#coding:utf-8
#author:LiaoPan
#date:2024/10/15 21:48

"""
指定目录，遍历子文件夹下fif文件，并画出所有*.fif文件的头动轨迹，并绘制出图。
"""
import sys
import mne
from mne.io import read_raw
from mne.chpi import compute_head_pos,get_chpi_info,compute_chpi_amplitudes,compute_chpi_locs
from mne.viz import plot_head_positions,plot_chpi_snr
from pathlib import Path
from joblib import Parallel,delayed
import matplotlib.pyplot as plt


def visual_headmov(fname,out_dir):
    """
    ref: https://mne.tools/stable/auto_tutorials/preprocessing/59_head_positions.html
    """
    try:
        fname = Path(fname)
        output_fname_traces = out_dir / fname.parent.name / f"{fname.stem}_traces.png" 
        output_fname_field = out_dir / fname.parent.name / f"{fname.stem}_field.png" 
        output_fname_snr = out_dir / fname.parent.name / f"{fname.stem}_chpi_snr.png" 
        
        if output_fname_field.exists() and output_fname_field.exists() and output_fname_snr.exists():
            print(f"{fname.parent.name}'s headmovement alread exists,skipping...")
            sys.exit()
        else:
            raw = read_raw(fname,preload=True,allow_maxshield=True)
            chpi_amplitudes = compute_chpi_amplitudes(raw,verbose=True)
            chpi_locs = compute_chpi_locs(raw.info, chpi_amplitudes,adjust_dig=True,verbose=True)
            head_pos = compute_head_pos(raw.info, chpi_locs,adjust_dig=True,verbose=True)

            if not output_fname_traces.parent.exists():
                output_fname_traces.parent.mkdir()
            
            if not output_fname_traces.exists():    
                fig_traces = plot_head_positions(head_pos,mode="traces")  
                fig_traces.savefig(output_fname_traces)
            
            if not output_fname_field.exists():
                fig_field = plot_head_positions(head_pos,mode="field")
                fig_field.savefig(output_fname_field)
            
            if not output_fname_snr.exists():
                snr_dict = mne.chpi.compute_chpi_snr(raw)
                fig_snr_hpi = plot_chpi_snr(snr_dict)
                fig_snr_hpi.savefig(output_fname_snr)
    except Exception as e:
        print(f"{fname} error:",e)


def main(root_dir,out_dir):
    
    fif_files = [fif for fif in list(root_dir.rglob("*.fif")) if 'tsss' not in fif.name]
    results = Parallel(n_jobs=-1)(delayed(visual_headmov)(fif_file,out_dir) for fif_file in fif_files)
      
if __name__=="__main__":    
    root_dir = Path("/data/datasets")
    headmv_out_dir = Path("/data/headmove")
    
    if not headmv_out_dir.exists():
        headmv_out_dir.mkdir()
    
    main(root_dir,out_dir=headmv_out_dir)
    
    
