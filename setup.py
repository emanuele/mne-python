#! /usr/bin/env python
#
# Copyright (C) 2011 Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>

import os
import mne

import setuptools  # we are using a setuptools namespace
from numpy.distutils.core import setup

descr = """MNE python project for MEG and EEG data analysis."""

DISTNAME            = 'mne'
DESCRIPTION         = descr
MAINTAINER          = 'Alexandre Gramfort'
MAINTAINER_EMAIL    = 'gramfort@nmr.mgh.harvard.edu'
URL                 = 'http://martinos.org/mne'
LICENSE             = 'BSD (3-clause)'
DOWNLOAD_URL        = 'http://github.com/mne-tools/mne-python'
VERSION             = mne.__version__


if __name__ == "__main__":
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    setup(name=DISTNAME,
          maintainer=MAINTAINER,
          include_package_data=True,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          version=VERSION,
          download_url=DOWNLOAD_URL,
          long_description=open('README.rst').read(),
          zip_safe=False,  # the package can run out of an .egg file
          classifiers=['Intended Audience :: Science/Research',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved',
                       'Programming Language :: Python',
                       'Topic :: Software Development',
                       'Topic :: Scientific/Engineering',
                       'Operating System :: Microsoft :: Windows',
                       'Operating System :: POSIX',
                       'Operating System :: Unix',
                       'Operating System :: MacOS'],
          platforms='any',
          packages=['mne', 'mne.tests',
                    'mne.beamformer', 'mne.beamformer.tests',
                    'mne.connectivity', 'mne.connectivity.tests',
                    'mne.data',
                    'mne.datasets',
                    'mne.datasets.sample',
                    'mne.datasets.megsim',
                    'mne.fiff', 'mne.fiff.tests',
                    'mne.fiff.bti', 'mne.fiff.bti.tests',
                    'mne.fiff.kit', 'mne.fiff.kit.tests',
                    'mne.layouts', 'mne.layouts.tests',
                    'mne.minimum_norm', 'mne.minimum_norm.tests',
                    'mne.mixed_norm',
                    'mne.inverse_sparse', 'mne.inverse_sparse.tests',
                    'mne.preprocessing', 'mne.preprocessing.tests',
                    'mne.simulation', 'mne.simulation.tests',
                    'mne.tests',
                    'mne.transforms', 'mne.transforms.tests',
                    'mne.stats', 'mne.stats.tests',
                    'mne.time_frequency', 'mne.time_frequency.tests',
                    'mne.realtime', 'mne.realtime.tests', 'mne.decoding',
                    'mne.decoding.tests'],
          package_data={'mne': ['data/*.sel',
                                'data/icos.fif.gz',
                                'layouts/*.lout']},
          scripts=['bin/mne_clean_eog_ecg.py', 'bin/mne_flash_bem_model.py',
                   'bin/mne_surf2bem.py', 'bin/mne_compute_proj_ecg.py',
                   'bin/mne_compute_proj_eog.py', 'bin/mne_maxfilter.py',
                   'bin/mne_bti2fiff.py', 'bin/mne_kit2fiff.py',
                   'bin/mne_browse_raw.py', 'bin/mne_make_scalp_surfaces.py'])
