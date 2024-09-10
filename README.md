# BrainVision Core reader and writer

This is a Python implementation to read and write EEG data in the BrainVision Core data format as defined by [BrainProducts](https://www.brainproducts.com/) and as used in [BIDS](https://bids.neuroimaging.io/).

The BrainVision Core data format consists of three files: the `.vhdr` file with header information, the `.vmrk` with markers or events, and the data in a file that usually has the extension `.eeg`.

The information from the header and marker is not parsed but retained as a dictionary with strings. Below some examples are given to get for example the channel names as list

This implementation can read from 16 and 32 bit integer formats and 32 bit float formats. It supports multiplexed and vectorized orientations. The data is returned as a channels-by-samples Numpy array with float32 values.

## Example

```python
import brainvision

(vhdr, vmrk, eeg) = brainvision.read('test/input.vhdr')
# do something with the data ...

# parse the header
nchans = int(vhdr['Common Infos']['NumberOfChannels'])
labels = [item.split(',')[0] for item in vhdr['Channel Infos'].values()]
units  = [item.split(',')[3] for item in vhdr['Channel Infos'].values()]
print(nchans, labels, units)

# parse the markers
type        = [item.split(',')[0] for item in vmrk['Marker Infos'].values()]
description = [item.split(',')[1] for item in vmrk['Marker Infos'].values()]
sample      = [int(item.split(',')[2])-1 for item in vmrk['Marker Infos'].values()]   # in data points, 0-based
duration    = [int(item.split(',')[3])   for item in vmrk['Marker Infos'].values()]   # in data points
channel     = [int(item.split(',')[4])   for item in vmrk['Marker Infos'].values()]   # note that this is 1-based
print(type, description, sample, duration, channel)

# write it back to disk
brainvision.write('test/output.vhdr', vhdr, vmrk, eeg) 
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
- https://github.com/bids-standard/pybv/
- https://pybv.readthedocs.io/en/stable/
- https://github.com/fieldtrip/fieldtrip/blob/master/fileio/private/read_brainvision_vhdr.m 
- https://github.com/fieldtrip/fieldtrip/blob/master/fileio/private/read_brainvision_vmrk.m 
- https://github.com/fieldtrip/fieldtrip/blob/master/fileio/private/read_brainvision_eeg.m 
- https://github.com/bids-standard/pyedf/
