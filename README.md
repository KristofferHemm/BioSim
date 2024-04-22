## Project description

BioSim is a Python library for modelling the ecosystem of the Rossøya island over time. 
The fauna on the island consists of two species: Herbivores and Carnivores. 
Using this library will allow you to simulate how the fauna on the island evolves over time. 
The library allows the user to vary the conditions on the island, such as island shape and 
initial populations, to observe how changes in these conditions will affect the fauna over time.

The library has the posibility to graphically display the simulation over time, including the map of the island, heatmaps    that display the distribuition of each population on the island. In addidion, the total population count and population count for each specie is displayed as a graph. The fitness, age and weight for each specie are displayed in separate graphs. The complete simulation can be saved as a video. A video created from the example script sample_sim.py is displayed below.

https://github.com/KristofferHemm/BioSim/assets/167197952/63df4502-abf1-4ebd-92fe-33ca401e94d5



## Features
* Simulate 4 separate land types: Water, Lowland, Highland and Desert.
* Simulate 2 animal species: Herbivores and Carnivores.
* Support for visualization of the animal population and distribution across the island.
* Support for generating a mp4 video of the simulation.
* Support for configuration model parameters update mid-simulation.
* Support for adding additional animals mid-simulation.
* Support for exporting a log file of the simulation results.
* Support for saving and loading the simulation state


## Dependencies
The project was built on Python 3.8.  
The project depends on the following python packages. 
Dependencies should be automatically installed.
```
numpy
matplotlib
pandas
pytest
pytest-mocker
scipy
ffmpeg-python
```

## Installation

Clone the repository onto your machine. 
Use the package manager `pip` to install BioSim.

```shell
git clone https://github.com/KristofferHemm/biosim
cd biosim
pip install . --user
```

## Usage

```python
from biosim.simulation import BioSim

# Define the geography using a text string. 'W', 'L', 'H', 'D' define the different land types
geogr = 'WWW\nWLW\nWWW'

# Define the initial population of herbivores and carnivores
ini_herb = [{'loc': (2, 2),'pop': [{'species': 'Herbivore','age': 1, 'weight': 20} for _ in range(50)]}]

# Create a simulation object
sim = BioSim(island_map=geogr, ini_pop=ini_herb, seed=1234)

# Set parameters
sim.set_animal_parameters('Herbivore', {'xi': 1.5, 'omega': 0.5})
sim.set_landscape_parameters('L', {'f_max': 600})

# Simulate for the desired number of years
sim.simulate(num_years=10)
```
## Examples
Check out the [examples](https://github.com/KristofferHemm/biosim/tree/main/examples)
directory for usage example scripts. 


## HTML Documentation

To generate the html documentation using Sphinx, run the following command form the base directory.
```
cd docs
make html
```
The index.html file will be built at `_build/html/index.html`.


## Uninstallation

```shell
pip uninstall biosim
```

## Version history
* 1.1.0 (2022-01-18) - Added simulation state save/load
* 1.0.0 (2022-01-18) - First release

## Licence
BioSim is an open source software licensed under [The MIT License (MIT)](https://choosealicense.com/licenses/mit/).
