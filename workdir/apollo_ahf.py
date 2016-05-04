import os
import sys
from global import *

def run_ahf():
    for i in range(NSnaps):
        os.system("mkdir -p "+outputfolder+"/snap_%03d/"%(i))
        folder = outputfolder+"/snap_%03d/"%(i)
        inputfile = folder+"/config_snap%03d.txt"%(i)
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
        cmd = "qsub %s %s \"%s %s\"" % (submission_script,ahf_exec,inputfile,dvirlist)
        os.system(cmd)
def main():
    run_ahf()

if __name__ == "__main__":
    main()
    
