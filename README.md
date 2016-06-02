How to use this code?
======================

- Get the code:

       ```
       git clone https://github.com/boywert/ahf_MULTIDVIR
       cd ahf_MULTIDVIR
       ```

- Edit AHF-v1.0-088/Makefile.config and template/ahf.template according to the run and the system.

- Edit USERDVIR.list for the DVIR list

- Edit template/apollo_mpi.pbs (SGE) or create one for your system

- Edit template/apollo_single.pbs (SGE) or create one for your system

- Edit globals.py (python file containing parameters) 

- Compile AHF:
  	  ```
  	  make clean && make
	  ```
	  
- Run AHF (automated to do all snapshots):
  ```
  python run_ahf.py
  ```
	  
- Wait until all jobs in the queue completed. Now we have AHF catalogue of all snapshots and overdensities.

- Run makelink.py to link halos between overdensity groups and submit the merger graph linking into the system queue.
      ```
      python makelink.py
      ```
- Wait until all jobs in the queue completed. Now we have all linking required but they are still in internal format. To generate HDF5 file:
       ```
       python gen_hdf5.py
       ```
- Everything should be done.



