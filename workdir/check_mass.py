import os
import sys
import numpy
import subprocess
import fast3tree
import cPickle as pickle
import matplotlib.pyplot as plot
import matplotlib
matplotlib.rc('text', usetex=True)

prefix_input = "62.5_dm"
prefix_template = "62.5_halo_rho"
outputfolder = "/lustre/scratch/astro/cs390/codes/ahf-v1.0-084/workdir/halos"
mass_limit = 5.e12
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
    timetable = numpy.loadtxt("data_snaplist.txt")[:,4]
    halo_in = []
    pickle_file = "all_halos.pickled"
    if os.path.isfile(pickle_file) is False:
        for isnap in range(NSnaps):
            halo_in.append([])
            print "snap",isnap
            folder_B = outputfolder+"/snap_%03d/"%(isnap)
            for i in range(len(overdensities)):
                halo = numpy.loadtxt(folder_B+"/mergertrees/"+prefix_template+str(overdensities[i])+"halo.txt")
                if len(halo.shape) == 1:
                    halo.shape = (-1,43)
                halo_in[isnap].append(halo)
        pickle.dump(halo_in, open(pickle_file, "wb" ))
    else:
        print "loading pickled file",pickle_file
        halo_in = pickle.load(open(pickle_file, "rb" ))
    
    lastsnap = 61
    base_overden = 0
    count_core = 0
    count_main = 0
    count_sub = 0
    slot_number = 1000
    data_core= numpy.empty(slot_number,dtype=numpy.float32)
    data_main= numpy.empty(slot_number,dtype=numpy.float32)
    data_sub = numpy.empty(slot_number,dtype=numpy.float32)
    for iden in range(1):
        for ihalo in range(len(halo_in[lastsnap][iden])):
            halo = halo_in[lastsnap][iden][ihalo]
            mass_0 = halo[3]
            hi_halo = halo[0].astype(numpy.int64)
            if(hi_halo > -1):
                hi_halo_mass = halo_in[lastsnap][1][hi_halo,3]
                hi_halo_prog = halo_in[lastsnap][1][hi_halo,14].astype(numpy.int64)
            else:
                hi_halo_prog = -1
            pre_snap = lastsnap
            cur_snap = lastsnap-1
            prog = halo[14].astype(numpy.int64)
            
            while (prog > -1) & (cur_snap >= 0):
                a_cond = 0
                mass_new = halo_in[cur_snap][iden][prog,3]
                hi_prog = halo_in[cur_snap][iden][prog][0].astype(numpy.int64)
                if hi_prog > -1:
                    hi_prog_mass = halo_in[cur_snap][1][hi_prog,3]
                if hi_prog > -1 & hi_halo > -1:
                    if hi_halo_prog > -1:
                        if hi_prog != hi_halo_prog:
                            aaaaa=1
#count_miss += 1
                        else:
                            a_cond = 1
                            hi_alpha_a = numpy.arctan(numpy.log10(hi_halo_mass/hi_prog_mass)/numpy.log10(timetable[cur_snap]/timetable[pre_snap]))
                            #count_ok += 1
                        
                #alpha_a =  numpy.arctan((mass_0-mass_new)/(timetable[cur_snap]-timetable[pre_snap])/(mass_new + mass_0)*(timetable[cur_snap]+timetable[pre_snap]))
                alpha_a = numpy.arctan(numpy.log10(mass_0/mass_new)/numpy.log10(timetable[cur_snap]/timetable[pre_snap]))
                # if (mass_new > mass_limit) & (mass_0 > mass_limit):
                #     print alpha_a/numpy.pi
                mass_0 = mass_new
                old_hi_halo = hi_halo
                old_hi_halo_prog = hi_halo_prog
                hi_halo = hi_prog
                if(hi_halo > -1):
                    hi_halo_mass = halo_in[cur_snap][1][hi_halo,3]
                    hi_halo_prog = halo_in[cur_snap][1][hi_halo,14].astype(numpy.int64)
                else:
                    hi_halo_prog = -1
                prog = halo_in[cur_snap][iden][prog][14].astype(numpy.int64)
                pre_snap = cur_snap
                cur_snap -= 1
                
                if (prog > -1) & (cur_snap >= 0):
                    grand_mass = halo_in[cur_snap][iden][prog][3]
                    #alpha_b =  numpy.arctan((mass_new - grand_mass)/(timetable[cur_snap]-timetable[pre_snap])/(mass_new + grand_mass)*(timetable[cur_snap]+timetable[pre_snap]))
                    hi_grand_halo = halo_in[cur_snap][iden][prog][0].astype(numpy.int64)
                    alpha_b = numpy.arctan(numpy.log10(mass_new/grand_mass)/numpy.log10(timetable[cur_snap]/timetable[pre_snap]))
                    if(hi_grand_halo > -1):
                        hi_grand_mass = halo_in[cur_snap][1][hi_grand_halo,3]
                        hi_alpha_b = numpy.arctan(numpy.log10(hi_prog_mass/hi_grand_mass)/numpy.log10(timetable[cur_snap]/timetable[pre_snap]))

                    if (mass_new > mass_limit) & (mass_0 > mass_limit) & (grand_mass > mass_limit):
                        data_main[count_main] = numpy.fabs(alpha_a-alpha_b)/numpy.pi
                        count_main += 1
                        if count_main == len(data_main):
                            data_main.resize((count_main+slot_number))
                        if (a_cond == 1) & (hi_grand_halo > -1):
                            data_core[count_core] = numpy.fabs((alpha_a-alpha_b)/numpy.pi)/numpy.fabs((hi_alpha_a-hi_alpha_b)/numpy.pi)
                            count_core += 1
                            if(count_core == len(data_core)):
                                data_core.resize((count_core+slot_number))
                            
                            #print numpy.fabs(alpha_a-alpha_b)/numpy.pi,"none"
                        #print numpy.fabs((alpha_a-alpha_b)/numpy.pi)
    #print "miss",count_miss,"ok",count_ok
    for iden in range(1,2):
        for ihalo in range(len(halo_in[lastsnap][iden])):
            halo = halo_in[lastsnap][iden][ihalo]
            mass_0 = halo[3]
            pre_snap = lastsnap
            cur_snap = lastsnap-1
            prog = halo[14].astype(numpy.int64)
            
            while (prog > -1) & (cur_snap >= 0):
                mass_new = halo_in[cur_snap][iden][prog,3]
                alpha_a = numpy.arctan(numpy.log10(mass_0/mass_new)/numpy.log10(timetable[cur_snap]/timetable[pre_snap]))
                mass_0 = mass_new
                prog = halo_in[cur_snap][iden][prog][14].astype(numpy.int64)
                pre_snap = cur_snap
                cur_snap -= 1
                
                if (prog > -1) & (cur_snap >= 0):
                    grand_mass = halo_in[cur_snap][iden][prog][3]
                    #alpha_b =  numpy.arctan((mass_new - grand_mass)/(timetable[cur_snap]-timetable[pre_snap])/(mass_new + grand_mass)*(timetable[cur_snap]+timetable[pre_snap]))
                    
                    alpha_b = numpy.arctan(numpy.log10(mass_new/grand_mass)/numpy.log10(timetable[cur_snap]/timetable[pre_snap]))
                    
                    if (mass_new > mass_limit) & (mass_0 > mass_limit) & (grand_mass > mass_limit):
                        data_sub[count_sub] = numpy.fabs(alpha_a-alpha_b)/numpy.pi
                        count_sub += 1
                        if count_sub == len(data_sub):
                            data_sub.resize((count_sub+slot_number))
                    
    fig = plot.figure()
    ax = fig.add_subplot(111)
    data_core.resize((count_core))
    hist =  numpy.histogram(numpy.log10(data_core))
    ax.plot(hist[1][:len(hist[0])],numpy.cumsum(hist[0].astype(numpy.float32))/numpy.sum(hist[0]),label="%d samples"%(count_core))
    ax.set_xlabel(r'$\log_{10}(\xi_{200c}/\xi_{1000c})$')
    ax.set_ylabel(r'$P(<\log_{10}(\xi_{200c}/\xi_{1000c}))$')
    leg = ax.legend(loc='best', handlelength = 10,ncol=1, fancybox=True, prop={'size':10})
    leg.get_frame().set_linewidth(0)
    fig.savefig("xi_ratio.pdf")
    plot.close(fig)
    
    fig = plot.figure()
    ax = fig.add_subplot(111)
    data_main.resize((count_main))
    hist = numpy.histogram(data_main,bins=20)
    ax.plot(hist[1][:len(hist[0])],numpy.cumsum(1.*hist[0]/numpy.sum(hist[0])),label="200c, %d samples"%(count_main))
    ax.set_xlabel(r'$\pi^{-1}|\xi|$')
    ax.set_ylabel(r'$P(<\pi^{-1}|\xi|)$')
    #plot.show()
    data_sub.resize((count_sub))
    hist = numpy.histogram(data_sub,bins=20)
    ax.plot(hist[1][:len(hist[0])],numpy.cumsum(1.*hist[0]/numpy.sum(hist[0])),label="1000c, %d samples"%(count_sub))
    leg = ax.legend(loc='best', handlelength = 10,ncol=1, fancybox=True, prop={'size':10})
    leg.get_frame().set_linewidth(0)
    fig.savefig("xi_compare.pdf")
    print "count main", count_main
    print "count_sub", count_sub
    print "count_core", count_core
if __name__ == "__main__":
    main()

