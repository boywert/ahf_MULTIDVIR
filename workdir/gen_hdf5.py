import numpy
import os
import sys
import time
import h5py
import numpy.lib.recfunctions as rfn
from globals import *
struct_ahf_halos = numpy.dtype([
    ('haloID',numpy.int64,1),
    ('Mass',numpy.float32,1),
    ('Pos',numpy.float32,3)
])
struct_halo_share = numpy.dtype([
    ('haloID',numpy.int64,1),
    ('share',numpy.float32,1)
])
def get_nhalos(nsnaps,idens):
    nhalolist = numpy.zeros(nsnaps,dtype=numpy.int64)
    for isnap in range(nsnaps):
        filename = outputfolder+"/snap_%03d/"%(isnap)+"/multilevels/"+prefix_template+str(overdensities[idens])+"particle.txt"
        f = open(filename,"r")
        buf = f.readline()
        nhalolist[isnap] = long(buf)
        f.close()
    return nhalolist
def load_halocat(nsnaps,idens):
    nhalolist = get_nhalos(nsnaps,idens)
    totalhalo = numpy.sum(nhalolist,dtype = numpy.int64)
    firsthalo = numpy.cumsum(nhalolist,dtype=numpy.int64)-nhalolist
    halocat = numpy.empty(totalhalo,dtype = struct_ahf_halos)
    for isnap in range(nsnaps):
        if(nhalolist[isnap] > 0):
            filename = outputfolder+"/snap_%03d/"%(isnap)+"/multilevels/"+prefix_template+str(overdensities[idens])+"halo.txt"
            data = numpy.loadtxt(filename)
            if len(data.shape) == 1:
                data.shape = (1,43)
            halocat[firsthalo[isnap]:firsthalo[isnap]+nhalolist[isnap]]['haloID'] = data[:,0].astype(numpy.int64)
            halocat[firsthalo[isnap]:firsthalo[isnap]+nhalolist[isnap]]['Mass'] = data[:,3]
            for ihalo in range(nhalolist[isnap]):
                halocat[firsthalo[isnap]+ihalo]['Pos'] = data[ihalo,5:8]
    return (nhalolist,halocat)
def load_denrelation(nsnaps,idens):
    nhalolist = get_nhalos(nsnaps,idens)
    totalhalo = numpy.sum(nhalolist,dtype = numpy.int64)
    firsthalo = numpy.cumsum(nhalolist,dtype=numpy.int64)-nhalolist
    denscontainlist = numpy.zeros(totalhalo, dtype=numpy.int64)
    containlist = numpy.zeros(1000000,dtype=numpy.int64)
    counthalo = 0
    for isnap in range(nsnaps):
        if(nhalolist[isnap] > 0):
            filename = outputfolder+"/snap_%03d/"%(isnap)+"/multilevels/"+str(overdensities[idens])+"_to_"+str(overdensities[idens+1])+".txt"
            data = open(filename,"r").readlines()
            for iline in range(len(data)):
                in_data = data[iline].split()
                denscontainlist[firsthalo[isnap]+iline] = len(in_data)-1
                for icol in range(1,len(in_data)):
                    if counthalo == len(containlist):
                        containlist.resize((len(containlist+1000000)))
                    containlist[counthalo] = long(in_data[icol].strip())
                    counthalo += 1
    containlist.resize((counthalo))
    return (denscontainlist,containlist)

def load_desc(nsnaps,idens):
    nhalolist = get_nhalos(nsnaps,idens)
    totalhalo = numpy.sum(nhalolist,dtype = numpy.int64)
    firsthalo = numpy.cumsum(nhalolist,dtype=numpy.int64)-nhalolist
    desc = numpy.empty(1000000,dtype = struct_halo_share)
    descnlist = numpy.zeros(totalhalo, dtype=numpy.int64)
    counthalo = 0
    for isnap in range(nsnaps-1):
        if(nhalolist[isnap] > 0):
            filename = outputfolder+"/snap_%03d/"%(isnap)+"/multilevels/"+prefix_template+str(overdensities[idens])+"_fw_mtree"
            with open(filename,"r") as f:
                # skip 2 header lines
                buffer = f.readlines()
                print buffer
                #     if not buffer: break
                #     data = buffer.split()
                #     hid = long(data[0].strip())
                #     ndesc = long(data[2].strip())
                #     descnlist[firsthalo[isnap]+hid] = ndesc
                #     print data
                #     for i in range(ndesc):
                #         buffer = f.read()
                #         data_d = buffer.split()
                #         if counthalo == len(desc):
                #             desc.resize((len(desc+1000000)))
                #         desc[counthalo] = (long(data[1].strip()),float(data[0].strip()))
                #         counthalo += 1
    desc.resize((counthalo))
    print descnlist,desc
    return (descnlist,desc)
def load_prog(nsnaps,idens):
    return (prognlist,prog)
                    
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
    dens_array = numpy.array(overdensities)
    nlevels = len(overdensities)
    denslevel_grp = f.create_group("DensityLevels")
    denslevel_grp.attrs['NLevels'] = numpy.int32(nlevels)
    denslevel_level = denslevel_grp.create_dataset('DensLevel', data=dens_array)
    
    #Group -- Snapshot
    snapshot_grp = f.create_group("Snapshots")
    (nsnaps,snapshot_data) = load_snapshot(alistfile)
    #NSnap
    snapshot_grp.attrs['NSnap'] = numpy.int32(nsnaps)
    #Snap
    snapshot_snap = snapshot_grp.create_dataset('Snap', data=snapshot_data)

    # #Group -- HaloCatalogue
    # halocat_grp = []
    # for idens in range(len(overdensities)):
    #     halocat_grp.append(f.create_group("HaloCatalogue_"+str(idens)))
    #     (nhalolist,halocat) = load_halocat(nsnaps,idens)
    #     halosnap_snap = halocat_grp[idens].create_dataset('HalosInSnap', data=nhalolist)
    #     halocat_snap = halocat_grp[idens].create_dataset('Halos', data=halocat)
        
    #Group -- DensRelation
    # densrelation_grp = []
    # for idens in range(len(overdensities)-1):
    #     densrelation_grp.append(f.create_group("DensRelation_"+str(idens)))
    #     (denscontainlist,containlist) = load_denrelation(nsnaps,idens)
    #     denrelationlist_list = densrelation_grp[idens].create_dataset("NHalosContained", data=denscontainlist)
    #     denrelation_list = densrelation_grp[idens].create_dataset("HalosContained", data=containlist)        
    
    #Group -- Descendants
    descendants_grp = []
    for idens in range(len(overdensities)-1):
        descendants_grp.append(f.create_group("Descendant_"+str(idens)))
        (descendantlist,descendant) = load_desc(nsnaps,idens)
        descendantlist_list = descendants_grp[idens].create_dataset("NHalosDescendant", data=descendantlist)
        descendant_list = descendants_grp[idens].create_dataset("HalosDescendant", data=descendant)      

    #Group -- Descendants
    


def main():
    convert()
if __name__ == "__main__":
    main()    
