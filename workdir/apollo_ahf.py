import os
import sys

template = "/lustre/scratch/astro/cs390/codes/ahf_MULTIDVIR/workdir/ahf.template"
simfolder = "/lustre/scratch/astro/cs390/SUSSING2013_DATA/62.5_ori/"
prefix_input = "62.5_dm"
prefix_template = "62.5_dm"
outputfolder = "/lustre/scratch/astro/cs390/codes/ahf_MULTIDVIR/workdir/halos"
NSnaps = 62
submission_script = "/lustre/scratch/astro/cs390/codes/ahf_MULTIDVIR/workdir/runmpi.pbs"
exec_file = "/lustre/scratch/astro/cs390/codes/ahf_MULTIDVIR/bin/AHF-v1.0-084"
dvirlist = "/lustre/scratch/astro/cs390/codes/ahf_MULTIDVIR/workdir/USERDVIR.list"
for i in range(NSnaps):
    os.system("mkdir -p "+outputfolder+"/snap_%03d/"%(i))
    folder = outputfolder+"/snap_%03d/"%(i)+"/"+str(rho)
    inputfile = folder+"/config_snap%03d_%d.txt"%(i,rho)
    os.system("mkdir -p "+folder)
    ic_filename = simfolder+"/snapdir_%03d/"%(i) + prefix_input+"_%03d."%(i)
    outfile_prefix = folder+"/"+prefix_template
    f = open(inputfile,"w")
    print >> f, "[AHF]"
    print >> f, "ic_filename =",ic_filename
    print >> f, "outfile_prefix =",outfile_prefix
    print >> f, "Dvir = 200.0"
    f.close()
    os.system("cat "+template+" >> "+inputfile)
    cmd = "qsub %s %s %s %s" % (submission_script,exec_file,inputfile,dvirlist)
    os.system(cmd)
