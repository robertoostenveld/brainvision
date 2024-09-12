# Read and write EEG data in the BrainVision Core data format

This is a Python implementation to read and write EEG data in the BrainVision Core data format as defined by [BrainProducts](https://www.brainproducts.com/) and as used in [BIDS](https://bids.neuroimaging.io/).

The BrainVision Core data format consists of three files: the `.vhdr` file with header information, the `.vmrk` with markers or events, and the data in a file that usually has the extension `.eeg`. All files have to be in the same folder.

The information from the header and marker is not parsed but retained as a dictionary with strings. Below some examples are given to get for example the channel names as list

This implementation can read from 16 and 32 bit integer formats and 32 bit float formats. It supports multiplexed and vectorized orientations. The data is returned as a channels-by-samples Numpy array with float32 values.

## Example

The following example reads data from disk.

```python
import brainvision

# read the data
(vhdr, vmrk, eeg) = brainvision.read('test/input.vhdr')

# check the size of the data
(nchans, nsamples) = eeg.shape
print(nchans, nsamples)

# parse the header
nchans = int(vhdr['Common Infos']['NumberOfChannels'])
fsample = 1000000.0 / float(vhdr['Common Infos']['SamplingInterval'])
labels = [item.split(',')[0] for item in vhdr['Channel Infos'].values()]
units  = [item.split(',')[3] for item in vhdr['Channel Infos'].values()]
print(nchans, fsample, labels, units)

# parse the markers
type        = [item.split(',')[0] for item in vmrk['Marker Infos'].values()]
description = [item.split(',')[1] for item in vmrk['Marker Infos'].values()]
sample      = [int(item.split(',')[2])-1 for item in vmrk['Marker Infos'].values()]   # in data points, 0-based
duration    = [int(item.split(',')[3])   for item in vmrk['Marker Infos'].values()]   # in data points
channel     = [int(item.split(',')[4])   for item in vmrk['Marker Infos'].values()]   # note that this is 1-based
print(type, description, sample, duration, channel)
```

The following example constructs data from scratch and writes it to disk. Upon writing the header and markerfile, the vhdr and vmrk dictionaries will be validated to ensure that they contain the required fields.

```python
import numpy as np
import brainvision

vhdr = {'Common Infos': {'Codepage': 'UTF-8', 'DataFile': 'output.eeg', 'MarkerFile': 'output.vmrk', 'DataFormat': 'BINARY', 'DataOrientation': 'MULTIPLEXED', 'NumberOfChannels': '1', 'SamplingInterval': '1000'}, 'Binary Infos': {'BinaryFormat': 'FLOAT_32'}, 'Channel Infos': {'Ch1': '1,,0.5,µV'}}

vmrk = {'Common Infos': {'Codepage': 'UTF-8', 'DataFile': 'output.eeg'}, 'Marker Infos': {'Mk1': 'New Segment,,1,1,0'}}

nchans = 1
nsamples = 1000
rng = np.random.default_rng()
eeg = rng.standard_normal((nchans, nsamples))

# write the data
brainvision.write('output.vhdr', vhdr, vmrk, eeg) 
```

## Known limitations

This implementation currently cannot read ASCII data.

This implementation currently cannot deal with little to big endian conversions, hence reading and writing the binary data is only supported on little endian architectures. Apple silicon and Intel-based Mac computers are both little endian. Also Raspberry PI's ARM and Intel NUC's processors are little endian.

## Copyright

Copyright (C) 2024, Robert Oostenveld

This code is dual-licensed under the BSD 3-Clause "New" or "Revised" License and under the GPLv3 license, the choice is up to you.

When you make changes/iomprovements, please share them back to us so that others benefit as well.

## Acknowledgements

The test data that is included to demonstrate the functionality and to test the reading and writing originates from the pybv package.

## See also

- https://www.brainproducts.com/support-resources/brainvision-core-data-format-1-0/
- https://pybv.readthedocs.io/en/stable/
- https://github.com/bids-standard/pybv/
- https://github.com/bids-standard/pyedf/
- https://github.com/fieldtrip/fieldtrip/blob/master/fileio/private/read_brainvision_vhdr.m 
- https://github.com/fieldtrip/fieldtrip/blob/master/fileio/private/read_brainvision_vmrk.m 
- https://github.com/fieldtrip/fieldtrip/blob/master/fileio/private/read_brainvision_eeg.m 
