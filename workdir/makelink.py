import os
import sys
import numpy
import subprocess
import fast3tree
from globals import *

def get_z(prefix):
    filename = prefix+".parameter"
    a = float(subprocess.check_output(["grep","^a ",filename]).split()[1])
    z = 1./a - 1
    return z
def get_nhalos(prefix,z):
    nhalolist = numpy.zeros(files_per_snap,dtype=numpy.int64)
    for i in range(files_per_snap):
        filename = prefix+".%04d.z%5.3f.AHF_particles"%(i,z)
        f = open(filename,"r")
        buf = f.readline()
        nhalolist[i] = long(buf)
        f.close()
    return nhalolist
def read_ahf_halos_snap(prefix,z):
    nhalos = get_nhalos(prefix,z)*Ncol
    cumuhalos = numpy.cumsum(nhalos)
    firsthalos = cumuhalos - nhalos
    halos = numpy.empty(numpy.sum(nhalos))
    pids = []
    counthalo = 0
    for i in range(files_per_snap):
        if(nhalos[i] > 0):
            filename = prefix+".%04d.z%5.3f.AHF_halos"%(i,z)
            halo = numpy.loadtxt(filename)  
            halos[firsthalos[i]:cumuhalos[i]] = halo.flatten()
    halos.shape = (-1,Ncol)
    for i in range(files_per_snap):
        if(nhalos[i] > 0):
            filename = prefix+".%04d.z%5.3f.AHF_particles"%(i,z)
            (counthalo,pids) = read_ahf_particles(filename,counthalo,pids)
    if counthalo != len(halos):
        print "nhalos do not match",counthalo,len(nhalos)
        exit()
    return halos,pids
def read_ahf_halos(file):
    halos = numpy.loadtxt(file)
    return halos
def read_ahf_particles(filename,counthalo,pids):
    f = open(filename,"r")
    buf = f.readline()
    nhalo = long(buf)
    for i in range(nhalo):
        buf = f.readline()
        npart = long(buf.split()[0])
        #print "npart",npart
        pids.append(numpy.empty(npart,dtype=numpy.int64))
        for j in range(npart):
            buf = f.readline()
            pids[counthalo][j] = long(buf.split()[0])
            #print "\t",buf.split()[0]
        counthalo += 1
    return counthalo,pids
def main():
    for isnap in range(NSnaps):
        print "snap",isnap
        folder = outputfolder+"/snap_%03d/"%(isnap)
        ahf_halos = []
        rho = overdensities[0]
        desc_folder = outputfolder+"/snap_%03d/multidenshalos"%(isnap)
        outfile_prefix = folder+"/"+prefix_template+"_rho_%04d"%(long(rho+0.5))
        z =  get_z(outfile_prefix)
        get_nhalos(outfile_prefix,z)
        halos = []
        pids = []
        print "read halo catalogue"
        for rho in overdensities:
            (halo,pid) = read_ahf_halos_snap(outfile_prefix,z)
            halos.append(halo)
            pids.append(pid)
        for i in range(len(overdensities)-1):
            print "doing rho =",overdensities[i]
            lo_index = numpy.where(halos[i][:,1]==0)[0]
            lo_halos = halos[i][lo_index]
            hi_index = numpy.where(halos[i+1][:,1]==0)[0]
            hi_halos = halos[i+1][hi_index]
            lo_halos[:,0:2] = -1
            hi_halos[:,0:2] = -1
            for ih in range(len(lo_halos)):
                lo_halos[ih,0] = ih
            for ii in range(len(hi_halos)):
                hi_halos[ih,0] = ih
            os.system("mkdir -p "+folder+"/multilevels/")
            outfile = folder+"/multilevels/"+str(overdensities[i])+"_to_"+str(overdensities[i+1])+".txt"
            f = open(outfile,"w")
            if len(hi_halos) & len(lo_halos):
                pos = hi_halos[:,5:8]
                with fast3tree.fast3tree(pos) as tree:
                    tree.set_boundaries(0.0,boxsize_kpc)
                    tree.rebuild_boundaries()
                    for ii in range(len(lo_halos)):
                        h = lo_halos[ii]
                        idx = tree.query_radius(h[5:8],h[11], periodic=True,output='index')
                        if len(idx)>0:
                            string = "\t".join([str(id) for id in idx])
                            print >> f, "%d\t%s"%(ii,string)
                            hi_halos[idx,1] = ii
                del(tree)
                # pos = lo_halos[:,5:8]
                # with fast3tree.fast3tree(pos) as tree:
                #     tree.set_boundaries(0.0,boxsize_kpc)
                #     tree.rebuild_boundaries()
                #     for ii in range(len(hi_halos)):
                #         h = hi_halos[ii]
                #         idx = tree.query_radius(h[5:8],h[11], periodic=True,output='index')
                #         if len(idx)>0:
                #             if(idx[0]>=len(lo_halos)):
                #                 print "something is wrong, idx = ",idx,len(lo_halos)
                #             lo_halos[idx[0],0] = ii
                # del(tree)
            f.close()
            outfile = folder+"/multilevels/"+prefix_template+str(overdensities[i+1])+"halo.txt"
            numpy.savetxt(outfile,hi_halos)
            outfile = folder+"/multilevels/"+prefix_template+str(overdensities[i+1])+"particle.txt"
            f = open(outfile,"w+")
            print>>f, len(hi_index)
            for ihalo in hi_index:
                print>>f, ihalo,len(pids[i+1][ihalo]])
                string = "\n".join([str(id)+"\t1" for id in pids[i+1][ihalo]])
                print>>f,string
            f.close()
            if i == 0:
                outfile = folder+"/multilevels/"+prefix_template+str(overdensities[i])+"halo.txt"
                numpy.savetxt(outfile,lo_halos)
                outfile = folder+"/multilevels/"+prefix_template+str(overdensities[i])+"particle.txt"
                f = open(outfile,"w+")
                print>>f, len(lo_index)
                for ihalo in lo_index:
                    #print pids[i+1][ihalo]
                    print>>f, ihalo,len(pids[i][ihalo]])
                    string = "\n".join([str(id)+"\t1" for id in pids[i][ihalo]])
                    print>>f,string
                f.close()
if __name__ == "__main__":
    main()

