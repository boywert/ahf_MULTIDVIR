import os
import sys
import numpy
import subprocess
import fast3tree
prefix_input = "62.5_dm"
prefix_template = "62.5_halo_rho"
outputfolder = "/lustre/scratch/astro/cs390/codes/ahf-v1.0-084/workdir/halos"
NSnaps = 62
Ncol = 43
submission_script = "/lustre/scratch/astro/cs390/codes/ahf-v1.0-084/workdir/runmpi.pbs"
#overdensities = [200,500,1000,2500,5000,10000,20000]
overdensities = [200,1000]
files_per_snap = 16
datatype = 'i8,i8,i8,f4,i4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,f4,i4,f4,f4,f4,f4,f4,f4'
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
    idmap = numpy.empty(1+270**3,dtype=numpy.int32)
    for isnap in range(NSnaps-1):
        print "snap",isnap
        folder_A = outputfolder+"/snap_%03d/"%(isnap)
        folder_B = outputfolder+"/snap_%03d/"%(isnap+1)
        for i in range(len(overdensities)):
            print "rho=",overdensities[i]
            halos_A = numpy.loadtxt(folder_A+"/multilevels/"+prefix_template+str(overdensities[i])+"halo.txt")
            halos_B = numpy.loadtxt(folder_B+"/multilevels/"+prefix_template+str(overdensities[i])+"halo.txt")
            if (len(halos_A)>0) & (len(halos_B)>0):
                if len(halos_A.shape) == 1:
                    halos_A.shape = (1,43)
                if len(halos_B.shape) == 1:
                    halos_B.shape = (1,43)
                with open(folder_A+"/multilevels/"+prefix_template+str(overdensities[i])+"particle.txt", "r") as f:
                    pids_A = f.readlines()
                    for ii in range(len(pids_A)):
                        pids_A[ii] = [long(id) for id in pids_A[ii].split()]
                    f.close()
                with open(folder_B+"/multilevels/"+prefix_template+str(overdensities[i])+"particle.txt", "r") as f:
                    pids_B = f.readlines()
                    for ii in range(len(pids_B)):
                        pids_B[ii] = [long(id) for id in pids_B[ii].split()]
                    f.close()
                print "halo_A",len(halos_A),len(pids_A)
                print "halo_B",len(halos_B),len(pids_B)
                idmap[:] = -1
                for ii in range(len(pids_B)):
                    for jj in pids_B[ii]:
                        idmap[jj] = ii
                halos_A[:,2] = -1
                halos_A[:,14] = -1
                for iii in range(len(pids_A)):
                    chooser = numpy.zeros(len(pids_B))
                    for jj in range(len(pids_A[iii])):
                        index = pids_A[iii][jj]
                        if idmap[index] > -1:
                            chooser[idmap[index]] += float(jj+1)**(-2./3) 
                    maxid = numpy.argmax(chooser)
                    if chooser[maxid] > 0:
                        #print iii,chooser[maxid]
                        halos_A[iii,2] = maxid
                os.system("mkdir -p "+ folder_A +"/mergertrees/")
                numpy.savetxt(folder_A+"/mergertrees/"+prefix_template+str(overdensities[i])+"halo.txt", halos_A)
            else:
                os.system("mkdir -p "+ folder_A +"/mergertrees/")
                os.system("touch "+folder_A+"/mergertrees/"+prefix_template+str(overdensities[i])+"halo.txt")
            if isnap == NSnaps-2:
                halos_B[:,2] = -1
                halos_B[:,14] = -1
                os.system("mkdir -p "+folder_B+"/mergertrees/")
                numpy.savetxt(folder_B+"/mergertrees/"+prefix_template+str(overdensities[i])+"halo.txt", halos_B)
    for isnap in range(1,NSnaps):
        print "snap",isnap
        folder_A = outputfolder+"/snap_%03d/"%(isnap-1)
        folder_B = outputfolder+"/snap_%03d/"%(isnap)
        for i in range(len(overdensities)):
            print "rho=",overdensities[i]
            halos_A = numpy.loadtxt(folder_A+"/mergertrees/"+prefix_template+str(overdensities[i])+"halo.txt")
            halos_B = numpy.loadtxt(folder_B+"/mergertrees/"+prefix_template+str(overdensities[i])+"halo.txt")
            if (len(halos_A)>0) & (len(halos_B)>0):
                if len(halos_A.shape) == 1:
                    halos_A.shape = (1,43)
                if len(halos_B.shape) == 1:
                    halos_B.shape = (1,43)
                for ii in range(len(halos_B)):
                    index = numpy.where((halos_A[:,2].astype(numpy.int64)) == ii)[0]
                    if len(index):
                        p_index = numpy.argmax(halos_A[index,3])
                        halos_B[ii,14] = index[p_index]
                        halos_B[ii,15] = halos_A[index[p_index],3] 
                numpy.savetxt(folder_B+"/mergertrees/"+prefix_template+str(overdensities[i])+"halo.txt", halos_B)
if __name__ == "__main__":
    main()

