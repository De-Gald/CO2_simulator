import matlab.engine
import numpy as np

eng = matlab.engine.connect_matlab()


def save_csv(
    variable: str,
    formation: str
) -> None:
    array = eng.eval(f"load('{variable}.mat');")
    np.savetxt(f'formations/{formation}/{variable}.csv', array[variable], delimiter=',')
