# Setting for AHF parameter file
template = "/lustre/scratch/astro/cs390/codes/ahf_MULTIDVIR/workdir/ahf.template"


# The location of N-Body file
# We are mainly using GADGET
simfolder = "/lustre/scratch/astro/cs390/SUSSING2013_DATA/62.5_ori/"


# Prefix of the GADGET file
prefix_input = "62.5_dm"


# The location of files produced by internal process (halo catalogue)
outputfolder = "halos"


# The output HDF5 file
network_file = "network.hdf5"


# Total number of snapshots
NSnaps = 62


# The list of overdensity to use (rho_critical) [see ]
overdensities = [200,1000]


# Total node to compute AHF = the total output files per snapshot from AHF 
files_per_snap = 16


# The boxsize in kpc/h
boxsize_kpc = 625000.0 

submission_script_mpi = "template/apollo_mpi.pbs"

submission_script_single = "template/apollo_single.pbs"

# The total column of AHF halo output (default = 43)
Ncol = 43

# Prefix of internal process (you can ignore it)
prefix_template = "62.5_dm"


# The location of executable files. This will be generated by default. (you can ignore it)
ahf_exec = "bin/AHF"
mergertree_exec = "bin/MergerTree"

# The location of CUSTOM_DVIR list for AHF (you can ignore it)
dvirlist = outputfolder+"/USERDVIR.list"


# The list of expansion rate of all snapshot (you can ignore this for GADGET)
alistfile = "template/alist.txt"
