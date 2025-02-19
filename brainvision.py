import os
import sys
import numpy as np

# Python implementation to read and write EEG data in the BrainVision Core data format
#
# Copyright (C) 2024, Robert Oostenveld

def read(filename):
    (root, ext) = os.path.splitext(filename)
    if ext != '.vhdr': # FIXME, what about upper and lower case?
        raise ValueError('Filename does not have the .vhdr extension')
    vhdr = read_vhdr(filename)
    path = os.path.dirname(filename)
    markerfile = os.path.join(path, vhdr['Common Infos']['MarkerFile'])
    datafile = os.path.join(path, vhdr['Common Infos']['DataFile']) 
    vmrk = read_vmrk(markerfile)    
    eeg  = read_eeg(datafile, vhdr)
    # validate the data that was read
    validate(vhdr, vmrk, eeg)
    return (vhdr, vmrk, eeg)


def write(filename, vhdr, vmrk, eeg):
    # validate the data that is to be written
    validate(vhdr, vmrk, eeg)
    if sys.byteorder != 'little':
        raise ValueError('This function is only implemented for little-endian systems')
    (root, ext) = os.path.splitext(filename)
    if ext != '.vhdr':
        raise ValueError('Filename does not have the .vhdr extension')
    # update the filenames in the header and marker file
    vhdr['Common Infos']['MarkerFile'] = os.path.basename(root) + '.vmrk'
    vhdr['Common Infos']['DataFile'] = os.path.basename(root) + '.eeg'
    vmrk['Common Infos']['DataFile'] = os.path.basename(root) + '.eeg'
    # update the binary format
    vhdr['Common Infos']['DataFormat'] = 'BINARY'
    vhdr['Common Infos']['DataOrientation'] = 'MULTIPLEXED'
    vhdr['Binary Infos']['BinaryFormat'] = 'IEEE_FLOAT_32'
    # update the calibration, which is not needed for the float32 representation 
    nchans = int(vhdr['Common Infos']['NumberOfChannels'])
    for ch in range(nchans):
        info = vhdr['Channel Infos']['Ch%d' % (ch+1)]
        parts = info.split(',') + ['µV'] # older files might not have the Unit field, default is µV
        (name, ref, resolution, unit) = parts[0:4]
        resolution = '1'
        vhdr['Channel Infos']['Ch%d' % (ch+1)] = ','.join((name, ref, resolution, unit))
    # write the header file
    with open(root + '.vhdr', 'w') as f:
        f.write('BrainVision Data Exchange Header File Version 1.0\n\n')
        for section in vhdr:
            f.write('[%s]\n' % section)
            for key in vhdr[section]:
                f.write('%s=%s\n' % (key, vhdr[section][key]))
            f.write('\n')
    # write the marker file
    with open(root + '.vmrk', 'w') as f:
        f.write('BrainVision Data Exchange Marker File Version 1.0\n\n')
        for section in vmrk:
            f.write('[%s]\n' % section)
            for key in vmrk[section]:
                f.write('%s=%s\n' % (key, vmrk[section][key]))
            f.write('\n')
    # update the binary data and write the EEG data file
    eeg = eeg.transpose().astype(np.float32, order='C', copy=False)
    eeg.tofile(root + '.eeg')
    return


def validate(vhdr, vmrk, eeg):
    # check that the required sections are present in the vhdr
    sections = ['Common Infos', 'Binary Infos', 'Channel Infos']
    for section in sections:
        if not section in vhdr:
            raise ValueError('%s section is missing in vhdr' % section)
    sections = ['Codepage', 'DataFile', 'DataFormat', 'DataOrientation', 'NumberOfChannels', 'SamplingInterval']
    for section in sections:
        if not section in vhdr['Common Infos']:
            raise ValueError('%s section is missing in Common Infos' % section)
    sections =  ['BinaryFormat']
    for section in sections:
        if not section in vhdr['Binary Infos']:
            raise ValueError('%s section is missing in Binary Infos' % section)
    nchans = int(vhdr['Common Infos']['NumberOfChannels'])
    for ch in range(nchans):
        if not 'Ch%d' % (ch+1) in vhdr['Channel Infos']:
            raise ValueError('%s section is missing in Channel Infos' % section)
    # check consistency of certain values
    if not vhdr['Common Infos']['Codepage'] == 'UTF-8':
        raise ValueError('Unsupported codepage')
    if not vhdr['Common Infos']['DataFormat'] == 'BINARY':
        raise ValueError('Unsupported data format')
    if not vhdr['Common Infos']['DataOrientation'] == 'MULTIPLEXED':
        raise ValueError('Unsupported data orientation')
    if not vhdr['Binary Infos']['BinaryFormat'] in ['INT_16', 'INT_32', 'IEEE_FLOAT_32']:
        raise ValueError('Unsupported binary format')
    # check consistency between header and data
    nchans = int(vhdr['Common Infos']['NumberOfChannels'])
    if nchans != eeg.shape[0]:
        raise ValueError('Number of channels in header does not match data')
    # check that the required sections are present in the vmrk
    sections = ['Common Infos', 'Marker Infos']
    for section in sections:
        if not section in vmrk:
            raise ValueError('%s section is missing in vmrk' % section)
    sections = ['Codepage', 'DataFile']
    for section in sections:
        if not section in vmrk['Common Infos']:
            raise ValueError('%s section is missing in Common Infos' % section)


def read_vhdr(filename):
    vhdr = read_ini(filename)
    return vhdr


def read_vmrk(filename):
    vmrk = read_ini(filename)
    return vmrk


def read_eeg(filename, vhdr):
    if vhdr['Common Infos']['DataFormat'] != 'BINARY':
        raise ValueError('This function is only implemented for binary data')
    if sys.byteorder != 'little':
        raise ValueError('This function is only implemented for little-endian systems')
    if vhdr['Binary Infos']['BinaryFormat'] == 'INT_16':
        eeg = np.fromfile(filename, dtype=np.int16)
    elif vhdr['Binary Infos']['BinaryFormat'] == 'INT_32':
        eeg = np.fromfile(filename, dtype=np.int32)
    elif vhdr['Binary Infos']['BinaryFormat'] == 'IEEE_FLOAT_32':
        eeg = np.fromfile(filename, dtype=np.float32)
    else:
        raise ValueError('Unknown binary format')
    nchans = int(vhdr['Common Infos']['NumberOfChannels'])
    if vhdr['Common Infos']['DataOrientation'] == 'MULTIPLEXED':
        eeg = np.reshape(eeg, (nchans, -1), order='F')
    elif vhdr['Common Infos']['DataOrientation'] == 'VECTORIZED':
        eeg = np.reshape(eeg, (nchans, -1), order='C')
    else:
        raise ValueError('Unknown data orientation')
    # convert to 32 bit float
    eeg = eeg.astype(np.float32)
    # apply the calibration to get the actual values
    for ch in range(nchans):
        info = vhdr['Channel Infos']['Ch%d' % (ch+1)]
        parts = info.split(',') + ['µV'] # older files might not have the Unit field, default is µV
        (name, ref, resolution, unit) = parts[0:4]
        if resolution:
            eeg[ch] = eeg[ch] * float(resolution)
        else:
            print(f"Unknown resolution for '{filename}', defaulting to 1")
    return eeg


# The vhdr and vmrk file are almost fully conform to Windows INI files, but there are some
# deviations that make them incompatible with the ConfigParser and TOML parser.
def read_ini(filename):
    ini = {}
    section = 'unknown'
    with open(filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        # remove trailing whitespace
        line = line.strip()
        if line.startswith(';'):
            # this is a comment
            pass
        elif line.startswith('==') or line.startswith('--'):
            # this is formatting in the comment section
            pass
        elif line.startswith('['):
            # this is a section header
            section = line[1:-1].replace('Common infos', 'Common Infos')    # NeurOne BrainVision export workaround, e.g. as in: https://github.com/mne-tools/mne-testing-data/blob/master/Brainvision/test_NO.vhdr
            ini[section] = {}
        elif '=' in line:
            # this is a key=value pair
            (key, value) = line.split('=', 1)
            ini[section][key] = value
        else:
            # this is a blank line or a line that does not adhere to the expected formatting
            pass
    return ini

if __name__ == '__main__':
    (vhdr, vmrk, eeg) = read('test/test.vhdr')

    # parse the header
    nchans = int(vhdr['Common Infos']['NumberOfChannels'])
    fsample = 1000000.0 / float(vhdr['Common Infos']['SamplingInterval'])
    labels = [item.split(',')[0] for item in vhdr['Channel Infos'].values()]
    units  = [item.split(',')[3] for item in vhdr['Channel Infos'].values()]

    # parse the markers
    type        = [item.split(',')[0] for item in vmrk['Marker Infos'].values()]
    description = [item.split(',')[1] for item in vmrk['Marker Infos'].values()]
    sample      = [int(item.split(',')[2])-1 for item in vmrk['Marker Infos'].values()]   # in data points, 0-based
    duration    = [int(item.split(',')[3])   for item in vmrk['Marker Infos'].values()]   # in data points
    channel     = [int(item.split(',')[4])   for item in vmrk['Marker Infos'].values()]   # note that this is 1-based

    # look at the size of the data
    (nchans, nsamples) = eeg.shape

    print("-----------------------------------------------------------------")
    print('ORIGINAL FILE')
    print("-----------------------------------------------------------------")
    print(vhdr)
    print("-----------------------------------------------------------------")
    print(vmrk)
    print("-----------------------------------------------------------------")
    print(eeg)
    print("-----------------------------------------------------------------")

    # write the data back to a new file and read it again
    write('test/test1.vhdr', vhdr, vmrk, eeg)
    (vhdr1, vmrk1, eeg1) = read('test/test1.vhdr')
    print("-----------------------------------------------------------------")
    print('AFTER READING AND WRITING')
    print("-----------------------------------------------------------------")
    print(vhdr1)
    print("-----------------------------------------------------------------")
    print(vmrk1)
    print("-----------------------------------------------------------------")
    print(eeg1)
    print("-----------------------------------------------------------------")

    # compare the original file with the one that was just written
    if vhdr != vhdr1:
        raise ValueError('Header files do not match')
    if vmrk != vmrk1:
        raise ValueError('Marker files do not match')
    if not np.array_equal(eeg, eeg1):
        raise ValueError('EEG data files do not match')

    print('ALL TESTS PASSED')
    print("-----------------------------------------------------------------")

    # clean up the temporary files
    os.remove('test/test1.vhdr')
    os.remove('test/test1.vmrk')
    os.remove('test/test1.eeg')
