"""
==================================
Compute ICA components on raw data
==================================

ICA is used to decompose raw data in 49 to 50 sources.
The source matching the ECG is found automatically
and displayed. Subsequently, the cleaned data is compared
with the uncleaned data. The last section shows how to export
the sources into a fiff file for further processing and displaying, e.g.
using mne_browse_raw.

"""
print __doc__

# Authors: Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>
#          Denis Engemann <d.engemann@fz-juelich.de>
#
# License: BSD (3-clause)

import numpy as np
import pylab as pl

import mne
from mne.fiff import Raw
from mne.preprocessing.ica import ICA
from mne.datasets import sample
from mne.filter import band_pass_filter

###############################################################################
# Setup paths and prepare raw data

data_path = sample.data_path()
raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'

raw = Raw(raw_fname, preload=True)

picks = mne.fiff.pick_types(raw.info, meg=True, eeg=False, eog=False,
                            stim=False, exclude='bads')

###############################################################################
# Setup ICA seed decompose data, then access and plot sources.

# Instead of the actual number of components here we pass a float value
# between 0 and 1 to select n_components by a percentage of
# explained variance. Also we decide to use 64 PCA components before mixing
# back to sensor space. These include the PCA components supplied to ICA plus
# additional PCA components up to rank 64 of the MEG data.
# This allows to control the trade-off between denoising and preserving signal.

ica = ICA(n_components=0.90, n_pca_components=None, max_pca_components=100,
          random_state=0)

# 1 minute exposure should be sufficient for artifact detection.
# However, rejection performance may significantly improve when using
# the entire data range

# decompose sources for raw data using each third sample.
ica.decompose_raw(raw, picks=picks, decim=3)
print ica

# plot reasonable time window for inspection
start_plot, stop_plot = 100., 103.
ica.plot_sources_raw(raw, range(30), start=start_plot, stop=stop_plot)

###############################################################################
# Automatically find the ECG component using correlation with ECG signal.

# First, we create a helper function that iteratively applies the pearson
# correlation function to sources and returns an array of r values
# This is to illustrate the way ica.find_sources_raw works. Actually, this is
# the default score_func.

from scipy.stats import pearsonr
corr = lambda x, y: np.array([pearsonr(a, y.ravel()) for a in x])[:, 0]

# As we don't have an ECG channel we use one that correlates a lot with heart
# beats: 'MEG 1531'. To improve detection, we filter the the channel and pass
# it directly to find sources. The method then returns an array of correlation
# scores for each ICA source.

ecg_ch_name = 'MEG 1531'
l_freq, h_freq = 8, 16
ecg = raw[[raw.ch_names.index(ecg_ch_name)], :][0]
ecg = band_pass_filter(ecg, raw.info['sfreq'], l_freq, h_freq)
ecg_scores = ica.find_sources_raw(raw, target=ecg, score_func=corr)

# get maximum correlation index for ECG
ecg_source_idx = np.abs(ecg_scores).argmax()
title = 'ICA source matching ECG'
ica.plot_sources_raw(raw, ecg_source_idx, title=title, stop=3.0)

# let us have a look which other components resemble the ECG.
# We can do this by reordering the plot by our scores using order
# and generating sort indices for the sources:

ecg_order = np.abs(ecg_scores).argsort()[::-1][:30]  # ascending order

ica.plot_sources_raw(raw, ecg_order, start=start_plot, stop=stop_plot)

# Let's make our ECG component selection more liberal and include sources
# for which the variance explanation in terms of \{r^2}\ exceeds 5 percent.
# we will directly extend the ica.exclude list by the result.

ica.exclude.extend(np.where(np.abs(ecg_scores) ** 2 > .05)[0])

###############################################################################
# Automatically find the EOG component using correlation with EOG signal.

# As we have an EOG channel, we can use it to detect the source.

eog_scores = ica.find_sources_raw(raw, target='EOG 061', score_func=corr)

# get maximum correlation index for EOG
eog_source_idx = np.abs(eog_scores).argmax()

# plot the component that correlates most with the EOG
title = 'ICA source matching EOG'
ica.plot_sources_raw(raw, eog_source_idx, title=title, stop=3.0)

# plot spatial sensitivities of EOG and ECG ICA components
title = 'Spatial patterns of ICA components for ECG+EOG (Magnetometers)'
source_idx = range(15)
ica.plot_topomap([ecg_source_idx, eog_source_idx], ch_type='mag')
pl.suptitle(title, fontsize=12)

###############################################################################
# Show MEG data before and after ICA cleaning.

# We now add the eog artifacts to the ica.exclusion list
ica.exclude += [eog_source_idx]

# Restore sensor space data
raw_ica = ica.pick_sources_raw(raw, include=None)

start_compare, stop_compare = raw.time_as_index([100, 106])

data, times = raw[picks, start_compare:stop_compare]
data_clean, _ = raw_ica[picks, start_compare:stop_compare]

pl.figure()
pl.plot(times, data.T)
pl.xlabel('time (s)')
pl.xlim(100, 106)
pl.ylabel('Raw MEG data (T)')
y0, y1 = pl.ylim()

pl.figure()
pl.plot(times, data_clean.T)
pl.xlabel('time (s)')
pl.xlim(100, 106)
pl.ylabel('Denoised MEG data (T)')
pl.ylim(y0, y1)
pl.show()

###############################################################################
# Compare the affected channel before and after ICA cleaning.

affected_idx = raw.ch_names.index(ecg_ch_name)

# plot the component that correlates most with the ECG
pl.figure()
pl.plot(times, data[affected_idx], color='k')
pl.title('Affected channel MEG 1531 before cleaning.')
y0, y1 = pl.ylim()

# plot the component that correlates most with the ECG
pl.figure()
pl.plot(times, data_clean[affected_idx], color='k')
pl.title('Affected channel MEG 1531 after cleaning.')
pl.ylim(y0, y1)
pl.show()

###############################################################################
# Export ICA as raw for subsequent processing steps in ICA space.

from mne.layouts import make_grid_layout

ica_raw = ica.sources_as_raw(raw, start=100., stop=160., picks=None)

print ica_raw.ch_names[:5]  # just a few

ica_lout = make_grid_layout(ica_raw.info)

# Uncomment the following two lines to save sources and layout.
# ica_raw.save('ica_raw.fif')
# ica_lout.save(os.path.join(os.environ['HOME'], '.mne/lout/ica.lout'))

###############################################################################
# To save an ICA session you can say:
# ica.save('my_ica.fif')
#
# You can later restore the session by saying:
# >>> from mne.preprocessing import read_ica
# >>> read_ica('my_ica.fif')
#
# The ICA functionality exposed in this example will then be available at
# at any later point in time provided the data have the same structure as the
# data initially supplied to ICA.
