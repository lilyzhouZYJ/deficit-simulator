import logging
import sys
import os
from simulator import Simulator
import matplotlib.pyplot as plt

# def plot(simulator, deficits):
#     for deficits in simulator.deficit_tracker:
#         plt.plot(deficits)
#     plt.show()

def run(plot = False):
    if plot:
        logging.basicConfig(filename=f"log_file", encoding='utf-8', level=logging.ERROR)

        rows = 2
        cols = 3
        fig, axs = plt.subplots(rows, cols)

        for r in range(rows):
            for c in range(cols):
                simulator = Simulator(queue_count = 10)
                simulator.run(intervals = 500)

                for deficits in simulator.deficit_tracker:
                    axs[r, c].plot(deficits)
        
        plt.show()
    else:
        logging.basicConfig(filename=f"log_file", encoding='utf-8', level=logging.DEBUG)

        simulator = Simulator(queue_count = 10)
        simulator.run(intervals = 1000)

        for deficits in simulator.deficit_tracker:
            plt.plot(deficits)
        plt.show()

if __name__ == "__main__":
    # logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
    os.remove("log_file")

    # run(plot = True)
    run(plot = False)