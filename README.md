How to use this code?
======================

- Get the code:

       ```
       git clone https://github.com/boywert/ahf_MULTIDVIR
       cd ahf_MULTIDVIR
       ```

- Edit AHF-v1.0-088/Makefile.config and template/ahf.template according to the run and the system.

- Edit USERDVIR.list for the DVIR list

- Edit globals.py (python file containing parameters) 

- Compile AHF:
  	  ```
  	  make clean && make
	  ```
- Run AHF:
      ```
      mpirun -np [Ncpus] bin/AHF template/ahf.template USERDVIR.list
      ```




