#coding:utf-8
#author:liaopan
#date:2024/11/9 12:50
"""
修复被试第一个run1没采EOG信号，导致多个raw 进行concat时，会因为校正信息不对，导致无法正常concat；
即需要手动模拟一个EOG信号，并补充cals,dev_head_t等信息。
"""

import os,mne
import numpy as np
from pathlib import Path
from box import Box
from scipy.io import savemat
from mne.io.constants import FIFF

root_dir = Path("/data/")
data_path = root_dir / "datasets"


sub_path = root_dir / data_path / "sub01/241013" 

raw1 = mne.io.read_raw(sub_path / "sess1_run1_tsss_trans-bak.fif",verbose=False) # 原始run1，无EOG通道
raw2 = mne.io.read_raw(sub_path / "sess1_run2_tsss_trans.fif",verbose=False) # 原始run2，有EOG通道，用来校正run1的通道顺序；


# BIO001 chs Reference
bio_pos = [{'scanno': 1, 'logno': 1, 'kind': FIFF.FIFFV_BIO_CH, 
           'range': 0.00030517578125, 'cal': 0.0005438000080175698, 
           'coil_type': FIFF.FIFFV_COIL_EEG_BIPOLAR, 
           'loc': np.array([0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0., 1.]),
           'unit': FIFF.FIFF_UNIT_V, 'unit_mul': FIFF.FIFF_UNITM_NONE,
           'ch_name': 'BIO001', 'coord_frame': FIFF.FIFFV_COORD_UNKNOWN}]

raw1.load_data()
n_samples = raw1.n_times
zero_data = np.zeros((1,n_samples))

# Method1: not work! 无法保存修改后的cals，save后不对。(同方法二的问题)
# bio_info = create_info(ch_names=['BIO001'],sfreq=raw1.info['sfreq'], ch_types=['bio'],chan_info=bio_pos)
# bio_raw = mne.io.RawArray(zero_data, bio_info)
# print("bio_raw._cals:",bio_raw._cals[:10])
# raw = raw1.copy().add_channels([bio_raw], force_update_info=True)
# _,raw = mne.match_channel_orders([raw2,raw], copy=True)

# 完全新建一个数据。cals还是不对；
# 原因:改mne/_fiff/meas_info.py _write_ch_infos reset_range 注释掉；
# 解决办法：
# 只能通过修改源码方式解决：在mne/_fiff/meas_info.py _write_ch_infos函数中的变量reset_range部分注释掉；
# 注释掉此行代码，然后保存一个数据再改回来。
# 或者再write_info()函数中将reset_range修改为False，也可以；
#-------
# 如果还有问题，可以看看：
# mne/io/base.py _RawFidWriter 的init函数中，cfg.reset_range会将其重置为1.

## 方法二：
# ValueError: raws[1].info['dev_head_t'] differs. 
# The instances probably come from different runs, and are therefore associated with different head positions. Manually change info['dev_head_t'] to avoid this message but beware that this means the MEG sensors will not be properly spatially aligned. See mne.preprocessing.maxwell_filter to realign the runs to a common head position.
ch_names = ['BIO001']
ch_names.extend(raw1.info['ch_names'])
ch_type_raw = raw1.get_channel_types(raw1.info['ch_names'])
ch_types = ['bio']
ch_types.extend(ch_type_raw)
info = mne.create_info(ch_names=ch_names,ch_types=ch_types,sfreq=raw1.info['sfreq'])
positions = raw1.info['chs']
bio_pos.extend(positions)
info._unlocked = True
info['chs'] = bio_pos
info._unlocked = False
raw_data = np.concatenate([zero_data,raw1.get_data()],axis=0)
print("raw_data.shape",raw_data.shape)

raw = mne.io.RawArray(raw_data, info)
raw.info['dev_head_t'] = raw2.info['dev_head_t']
print("raw._cals:",raw._cals[:10],)

# 重新手动计算cals，供参考不需要使用。
# cals = [ch["cal"] * ch["range"] for ch in raw.info["chs"]]
# raw.info._unlocked=True
# for idx,ch in enumerate(raw.info["chs"]):
#     raw.info['chs'][idx]["cal"] = ch['cal']  
#     raw.info['chs'][idx]["range"] = ch['range']
#     # print("raw._cals",ch['cal']*ch['range'])
# raw.info._unlocked=False


run1_fname = sub_path / "sess1_run1_tsss_trans.fif"
# if os.path.exists(run1_fname):
#     os.remove(run1_fname)
raw.save(run1_fname,overwrite=False,verbose=True)

reload_raw = mne.io.read_raw(run1_fname,verbose=False)
print("reload_raw:",reload_raw.info['ch_names'][:10])
print(f"\ncheck run1 cals:{reload_raw._cals[:10]}---\n\nRef run2:{raw2._cals[:10]}",)
if all(reload_raw._cals == raw2._cals):
    print("The cals are all corrected! Congratulation!")
else:
    print("Wrong!Please Check.")
