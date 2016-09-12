AHF_FOLDER="AHF-v1.0-088"
all:
	mkdir -p bin
	cd ${AHF_FOLDER};\
	${MAKE} -C ${AHF_FOLDER};\
	${MAKE} MergerTree -C ${AHF_FOLDER};\
	ln -s ${AHF_FOLDER}/bin/${AHF_FOLDER} bin/AHF;\
	ln -s ${AHF_FOLDER}/bin/* bin/;\
	
	#cd bin;\
	#ln -s AHF-v1.0-088 AHF;\
	#cd ..
clean:
	rm -f bin/*;\
	cd ${AHF_FOLDER};\
	${MAKE} clean
