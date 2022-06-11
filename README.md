# CO2 simulator
Reservoir Simulator for long-term study of CO2 storage

## Installation on MacOS

1.	Download and Install Miniconda for Python 3:
curl https://repo.anaconda.com/miniconda/Miniconda3-py38_4.10.3-MacOSX-x86_64.sh' > Miniconda.sh
2.	Download CO2 storage simulator:
git clone https://github.com//De-Gald/CO2_simulator.git
3.	Go to the folder with the simulator:
cd CO2_simulator
4.	Create an environment named CO2_simulator, install Python 3.8: 
conda create --name CO2_simulator python=3.8
5.	Install all necessary dependencies:
pip install -r requirements.txt
6.	Install GNU Octave:
brew install octave
7. Run tests:
python -m unittest discover -s python/desktop/plotting -p '*_tests.py'
python -m unittest discover -s python/desktop/simulation -p '*_tests.py'
8.	Run the following command:
python gui.py
9.	Set the initial parameters and run the simulator in required mode.

## Installation on Windows

1.	Download and Install Miniconda for Python 3:
https://repo.anaconda.com/miniconda/Miniconda3-py38_4.10.3-Windows-x86_64.exe
2.	Download CO2 storage simulator:
git clone https://github.com//De-Gald/ReservoirSimulator.git
3.	Go to the folder with the simulator:
cd CO2_simulator
4.	Create an environment named CO2_simulator, install Python 3.8: 
conda create --name CO2_simulator python=3.8
5.	Install all necessary dependencies:
pip install -r requirements.txt
6.	Download and install GNU Octave:
https://ftpmirror.gnu.org/octave/windows/octave-6.4.0-w64-installer.exe
7. Run tests:
python -m unittest discover -s python/desktop/plotting -p '*_tests.py'
python -m unittest discover -s python/desktop/simulation -p '*_tests.py'
8.	Run the following command:
python gui.py
9.	Set the initial parameters and run the simulator in required mode.
