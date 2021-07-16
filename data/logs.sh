#!/bin/bash

for i in {1..8}
do
	mkdir -p "les-0$i/baseline"
	mkdir -p "les-0$i/planned"
	tar -xf "les-0$i/exp09/exp9-baseline-0$i.tar" -C  "les-0$i/baseline"
	tar -xf "les-0$i/exp09/exp9-planned-0$i.tar" -C  "les-0$i/planned"
	rm -r "les-0$i/exp09"
	mv "les-0$i/baseline/home/lesunb/morse_simulation/log" "les-0$i/baseline/"
	mv "les-0$i/planned/home/lesunb/morse_simulation/log" "les-0$i/planned/"
	rm -r "les-0$i/baseline/home"
	rm -r "les-0$i/planned/home"
	cp make_results_table.py "les-0$i/baseline/"
	cp make_results_table.py "les-0$i/planned/"
done
