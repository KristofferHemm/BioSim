import textwrap
import matplotlib.pyplot as plt
from biosim.simulation import BioSim

geogr = """\
           WWWWW
           WDLDW
           WLHLW
           WDLDW
           WWWWW"""
geogr = textwrap.dedent(geogr)

initial_fauna = [{'loc': (2, 3),
                  'pop': [{'species': 'Herbivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(50)]},
                 {'loc': (2, 3),
                  'pop': [{'species': 'Carnivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(20)]}]

seed = 1234
log_file = "data/logs.csv"
sim = BioSim(geogr, initial_fauna, seed=seed, vis_years=1, log_file=log_file)
sim.simulate(10)  # Simulate for 50 years

saved_json = sim.to_json()
# Save the state of simulation to a file.
# The state JSON will be saved at data/logs.json
sim.save_state()

# Load the BioSim state from a file and create a new object
sim2 = BioSim.load_state(log_file)
# Resume the simulation.
sim2.simulate(10)
plt.show(block=True)
