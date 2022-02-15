# IFCManipulations

Repository with the basic IFC manipulations for IFC files. And a IFC file viewer with pyQt5.

## prerequisites

Has anaconda installed on windows. And configured you system variables ($path) of anaconda on windows: 
* C:\ProgramData\Anaconda3
* C:\ProgramData\Anaconda3\Scripts
* C:\ProgramData\Anaconda3\Library\bin

## Instalation protocol

1. Clone the github repository.
```
$ git clone https://github.com/R-Rijnbeek/IFCManipulations.git
```

2. Enter the project folder.
```
$ cd IFCManipulations
```

3. Build the virtual environment on the repository by running:
```
$ build.bat
```

4. To activate the environmet and run the test scripts:
```
$ activate ./env
$ python /TEST/test.py
```

If it works. Then you can use the 'LASManippulation' module directory as a local package

## Notes to know: 

1. The dependencies to use all features of this repository are writed on the environmet.yml file: pylas, OCC, numpy
2. If you will only use the content of this repository. On a other proyect than you need to create an virtual environment that include "ifcopenshell", "OCC" and "pyQT5"
    * ANACONDA:
    ```
    conda install -c conda-forge pythonocc-core
    conda install -c conda-forge ifcopenshell
    ``` 
    * PIP:
    ```
    pip install PyQt5
    ```

3. This repository is tested with windows 10 and anaconda version 4.11.0.
