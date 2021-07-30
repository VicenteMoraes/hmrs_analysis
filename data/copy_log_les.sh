ssh les-01 'tar -czf - /home/lesunb/morse_simulation/log' | tar -xzf -
mkdir -p last_experiment/step2_execution/les-01
mv ./home/lesunb/morse_simulation/log/* last_experiment/step2_execution/les-01/

ssh les-02 'tar -czf - /home/lesunb/morse_simulation/log' | tar -xzf -
mkdir -p last_experiment/step2_execution/les-02
mv ./home/lesunb/morse_simulation/log/* last_experiment/step2_execution/les-02/

ssh les-03 'tar -czf - /home/lesunb/morse_simulation/log' | tar -xzf -
mkdir -p last_experiment/step2_execution/les-03
mv ./home/lesunb/morse_simulation/log/* last_experiment/step2_execution/les-03/

ssh les-04 'tar -czf - /home/lesunb/morse_simulation/log' | tar -xzf -
mkdir -p last_experiment/step2_execution/les-04
mv ./home/lesunb/morse_simulation/log/* last_experiment/step2_execution/les-04/

ssh les-05 'tar -czf - /home/lesunb/morse_simulation/log' | tar -xzf -
mkdir -p last_experiment/step2_execution/les-05
mv ./home/lesunb/morse_simulation/log/* last_experiment/step2_execution/les-05/

ssh les-06 'tar -czf - /home/lesunb/morse_simulation/log' | tar -xzf -
mkdir -p last_experiment/step2_execution/les-06
mv ./home/lesunb/morse_simulation/log/* last_experiment/step2_execution/les-06/

ssh les-07 'tar -czf - /home/lesunb/morse_simulation/log' | tar -xzf -
mkdir -p last_experiment/step2_execution/les-07
mv ./home/lesunb/morse_simulation/log/* last_experiment/step2_execution/les-07/

ssh les-08 'tar -czf - /home/lesunb/morse_simulation/log' | tar -xzf -
mkdir -p last_experiment/step2_execution/les-08
mv ./home/lesunb/morse_simulation/log/* last_experiment/step2_execution/les-08/