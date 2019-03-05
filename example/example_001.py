import mne
import numpy as np
import matplotlib.pyplot as plt
from mne.datasets import sample

data_path = sample.data_path()
raw_fname = data_path + '/MEG/sample/sample_audvis_raw.fif'
raw = mne.io.read_raw_fif(raw_fname)
print(raw)
print("sfreq:",raw.info['sfreq'])

def ch_names_to_types(ch_names):
    ch_types = []
    for ch in ch_names:
        _ch = int(ch[-1:])
        if _ch == 1:
            ch_types.append('mag')
        if _ch == 2 or _ch == 3:
            ch_types.append('grad')
    return ch_types

selection = mne.read_selection('Right-temporal')

ch_names = selection
ch_types = ch_names_to_types(ch_names)
print("ch_names",ch_names)
print("ch_types:",ch_types) #"kind must be one of ['ecg', 'bio', 'hbo', 'stim', 'eog', 'emg', 'ref_meg', 'misc', 'ecog', 'seeg', 'mag', 'eeg', 'grad', 'hbr']

sfreq = raw.info['sfreq']
picks = mne.pick_types(raw.info,meg=True,eeg=False,eog=False,
                      stim=False,selection=selection)
data, _ = raw[picks] 
info = mne.create_info(
    ch_names=ch_names,
    ch_types=ch_types,
    sfreq=sfreq
)

custom_raw = mne.io.RawArray(data, info)
custom_raw.plot(n_channels=39,scalings='auto')
plt.savefig('custom_raw_plot.png')
