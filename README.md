# CO2_simulator
Reservoir Simulator for long-term study of CO2 storage

## Installation on MacOS

1.	Download and Install Miniconda for Python 3:
curl https://repo.anaconda.com/miniconda/Miniconda3-py38_4.10.3-MacOSX-x86_64.sh' > Miniconda.sh
2.	Download CO2 storage simulator:
git clone https://github.com//De-Gald/ReservoirSimulator.git
3.	Go to the folder with the simulator:
cd ReservoirSimulator
4.	Create an environment named ReservoirSimulator, install Python 3.8: 
conda create --name ReservoirSimulator python=3.8
5.	Install all necessary dependencies:
pip install -r requirements.txt
6.	Install GNU Octave:
brew install octave
7.	Run the following command:
python gui.py
8.	Set the initial parameters and run the simulator in required mode.
