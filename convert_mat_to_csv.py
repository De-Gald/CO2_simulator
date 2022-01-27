import matlab.engine
import numpy as np

eng = matlab.engine.connect_matlab()


def save_csv(
    variable: str,
    formation: str
) -> None:
    array = eng.eval(f"load('{variable}.mat');")
    np.savetxt(f'formations/{formation}/{variable}.csv', array[variable], delimiter=',')


formations = [
    'brentgrp', 'brynefm', 'fensfjordfm', 'gassumfm', 'huginfmeast',
    'huginfmwest', 'johansenfm', 'krossfjordfm', 'pliocenesand',
    'sandnesfm', 'skadefm', 'sleipnerfm', 'sognefjordfm', 'statfjordfm',
    'ulafm', 'utsirafm', 'stofm', 'nordmelafm', 'tubaenfm',
    'bjarmelandfm', 'arefm', 'garnfm', 'tlefm', 'tiljefm']

names = ['colours', 'faces', 'vertices', 'faces_trapping', 'vertices_trapping']

formation = 'brentgrp'

for name in names:
    save_csv(name, formation)
