#coding:utf-8
import mne
raw = mne.io.read_raw("your fif file")
raw.load_data()

# 生成全零的模拟数据
n_samples = raw.n_times
zero_data = np.zeros((1,n_samples))
bio_info = mne.create_info(ch_names=['BIO001'],sfreq=raw.info['sfreq'], ch_types=['bio'])
bio_raw = mne.io.RawArray(zero_data, bio_info)
raw = raw_cat.copy().add_channels([bio_raw], force_update_info=True)

# 或者使用
mne.add_reference_channels('BIO001')


# 若通道顺序有误，可以校正
mne.match_channel_orders([ref_raw,raw], copy=False)
