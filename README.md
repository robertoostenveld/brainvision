# BrainVision reader and writer

This is a Python implementation to read and write EEG data in the BrainVision Core data format as defined by [BrainProducts](https://www.brainproducts.com/) and as used in [BIDS](https://bids.neuroimaging.io/).

The BrainVision Core data format consists of three files: the `.vhdr` file with header information, the `.vmrk` with markers or events, and the data in a file that usually has the extension `.eeg` but sometimes has the extension `.dat` or `.seg`.

Use as

```python
import brainvision

(vhdr, vmrk, eeg) = brainvision.read('test/input.vhdr')
# do something with the data ...

# write it back to disk
brainvision.write('test/output.vhdr', vhdr, vmrk, eeg) 
```

## Copyright

Copyright (C) 2024, Robert Oostenveld

This code is dual-licensed under the BSD 3-Clause "New" or "Revised" License and under the GPLv3 license, the choice is up to you. When you make changes/iomprovements, please share them back to us so that others benefit as well.

## Acknowledgements

The test data that is included to demonstrate the functionality and to test the reading and writing originates from the pybv package.

## See also

- https://www.brainproducts.com/support-resources/brainvision-core-data-format-1-0/
- https://github.com/bids-standard/pybv/
- https://pybv.readthedocs.io/en/stable/
- https://github.com/fieldtrip/fieldtrip/blob/master/fileio/private/read_brainvision_vhdr.m 
- https://github.com/fieldtrip/fieldtrip/blob/master/fileio/private/read_brainvision_vmrk.m 
- https://github.com/fieldtrip/fieldtrip/blob/master/fileio/private/read_brainvision_eeg.m 
- https://github.com/bids-standard/pyedf 
