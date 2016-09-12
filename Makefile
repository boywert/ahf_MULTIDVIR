AHF_FOLDER="AHF-v1.0-088"
all:
	mkdir -p bin
	cd ${AHF_FOLDER};\
	${MAKE};\
	${MAKE} MergerTree;\
	mv bin/* ../bin
	cd ..;\
	cd bin;\
	ln -s AHF-v1.0-088 AHF;\
	cd ..
clean:
	rm -f bin/*;\
	cd ${AHF_FOLDER};\
	${MAKE} clean
