AHF_FOLDER="AHF-v1.0-088"
all:
	mkdir -p bin
	cd ${AHF_FOLDER};\
	${MAKE};\
	${MAKE} MergerTree;\
	mv bin/* ../bin
clean:
	rm -f bin/*;\
	cd ${AHF_FOLDER};\
	${MAKE} clean
