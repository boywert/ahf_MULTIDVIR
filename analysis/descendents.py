# Add missing links to make tree search easier

import h5py
import numpy as np

nSnap=62

try:
    fin
except:
    fin=h5py.File('/Users/petert/data/Sussing/network.hdf5','r')
try:
    fout
except:
    fout=h5py.File('./network.hdf5','rw')

# Read in existing data about halos
HalosInSnap=fin['HaloCatalogue_0/HalosInSnap']
nHaloSnap=HalosInSnap[:]
nHalo=sum(nHaloSnap)

# Read in existing data about Descendants
NHalosDescendant=fin['Descendant_0/NHalosDescendant']
nDesc=NHalosDescendant[:]
HalosDescendant=fin['Descendant_0/HalosDescendant']
haloID=HalosDescendant['haloID']
share=HalosDescendant['share']
# Sanity checks
assert nHalo == len(nDesc)
assert sum(nDesc) == len(haloID)

# ahf_MULTIDVIR labels halos from 0 within each snap.
# To identify the location within the whole array, 
# we need to know the offsets of each snap.
# nHaloSnapCum provides the cumulative halo count needed to do that.

nHaloSnapCum=np.zeros(nSnap,dtype=np.int32)
nHaloSnapCum[0]=nHaloSnap[0]
for iSnap in range(1,nSnap): 
    nHaloSnapCum[iSnap]=nHaloSnapCum[iSnap-1]+nHaloSnap[iSnap]
assert nHaloSnapCum[nSnap-1] == nHalo

