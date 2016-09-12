AHF_FOLDER=AHF-v1.0-088
all: AHF MergerTree
AHF:
	mkdir -p bin
	${MAKE} -C ${AHF_FOLDER}
	ln -s ${AHF_FOLDER}/bin/${AHF_FOLDER} bin/AHF
MergerTree:
	mkdir -p bin
	${MAKE} MergerTree -C ${AHF_FOLDER}
	ln -s ${AHF_FOLDER}/bin/MergerTree bin/MergerTree
clean:
	rm -f bin/*
	${MAKE} clean -C ${AHF_FOLDER}
