import numpy
import os
import sys
import time
import h5py
import numpy.lib.recfunctions as rfn

struct_ahf_halos = numpy.dtype([
    ('haloID',numpy.int32,1)
    ('Mass',numpy.float32,1)
    ('Pos',numpy.float32,3)
])


def load_snapshot(alistfile):
    a = numpy.loadtxt(alistfile)
    nsnaps = len(a)
    print nsnaps
    print a
    return (nsnaps,a)
def convert():
    folder = "/Users/boywert/TestCodes/treedata/"
    f = h5py.File("network.hdf5", 'w')
    # Version
    f.attrs.create('Version', 1, dtype=numpy.int32)
    # Subversion
    f.attrs.create('Subversion', 1, dtype=numpy.int32)
    # Title
    f.attrs.create('Title', "Network test")
    # Description
    f.attrs.create('Description', "This is for testing")
    # BoxsizeMpc -- I'm not convinced that we should use Mpc instead Mpc/h (It's quite difficult to remember)
    # so I will use Mpc/h to avoid the errors from myself
    f.attrs.create('BoxsizeMpc_h', 62.5, dtype=numpy.float32)
    # OmegaBaryon
    f.attrs.create('OmegaBaryon', 0.044, dtype=numpy.float32)
    # OmegaCDM
    f.attrs.create('OmegaCDM', 0.27-0.044, dtype=numpy.float32)
    # H100
    f.attrs.create('H100', 0.704, dtype=numpy.float32)
    # Sigma8
    f.attrs.create('Sigma8', 0.807, dtype=numpy.float32)

    #Group -- Density Level
    dens = [200.0,1000.0]
    dens_array = numpy.array(dens)
    nlevels = len(dens)
    denslevel_grp = f.create_group("DensityLevels")
    denslevel_grp.attrs['NLevels'] = numpy.int32(nlevels)
    denslevel_level = snapshot_grp.create_dataset('DensLevel', data=dens_array)
    
    #Group -- Snapshot
    snapshot_grp = f.create_group("Snapshots")
    (nsnaps,snapshot_data) = load_snapshot(alistfile)
    #NSnap
    print numpy.int32(nsnaps)
    snapshot_grp.attrs['NSnap'] = numpy.int32(nsnaps)
    #Snap
    snapshot_snap = snapshot_grp.create_dataset('Snap', data=snapshot_data)
    
    
    #Group -- Descendants
    


def main():
    convert()
if __name__ == "__main__":
    main()    
