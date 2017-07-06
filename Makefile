.PHONY : all
all: install

.PHONY : build
build:
	python setup.py build

.PHONY : install
install:
	sudo python setup.py install
	
