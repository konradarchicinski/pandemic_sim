import networkx as nx 
import EoN
import matplotlib.animation as animation
import ffmpy
import argparse
from collections import defaultdict
from random import randint


def create_simulation(
    sim_name,
    sq_rate,
    qs_rate,
    it_rate, 
    si_rate,
    population_size, 
    initial_infection_number,
):

    matrix_size = int(round(population_size**(0.5)))
    G = nx.grid_2d_graph(matrix_size, matrix_size)

    initial_infections = [
        (randint(0, matrix_size), randint(0, matrix_size))
        for _ in range(initial_infection_number)
    ]

    H = nx.DiGraph()
    H.add_edge('Susc', 'Quar', rate = sq_rate)
    H.add_edge('Quar', 'Susc', rate = qs_rate)
    H.add_edge('Infe', 'Trea', rate = it_rate)
    H.add_edge('Trea', 'Quar', rate = 0.05)

    J = nx.DiGraph()
    J.add_edge(('Infe', 'Susc'), ('Infe', 'Infe'), rate = si_rate)

    IC = defaultdict(lambda:'Susc')
    for node in initial_infections:
        IC[node] = 'Infe'

    return_statuses = ['Susc', 'Infe', 'Trea', 'Quar']

    sim_kwargs = {
        'color_dict': {
            'Susc': '#5cb85c', 'Infe': '#d9534f', 'Trea': '#f0ad4e', 'Quar': '#0275d8'
        }, 
        'pos': {node:node for node in G}, 
        'tex': False
    }

    sim = EoN.Gillespie_simple_contagion(
        G, H, J, IC, 
        return_statuses, 
        tmax=150, 
        return_full_data=True, 
        sim_kwargs=sim_kwargs
    )

    produce_visualization(sim_name, sim, population_size)
    convert_video(sim_name)


def produce_visualization(sim_name, sim, population_size):
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=10, bitrate=1800)

    time, results = sim.summary()

    new_timeseries = (
        time, 
        {
            'Infected%': results['Infe']/population_size,
            'Treated%': results['Trea']/population_size,
            'qMargin': (results['Susc'] + results['Infe'] - results['Quar'])/population_size
        }
    )
    sim.add_timeseries(
        new_timeseries, 
        label = 'Simulation', 
        color_dict={'Infected': '#d9534f', 'Treated': '#f0ad4e', 'qMargin': '#292b2c'}
    )

    ani=sim.animate(ts_plots=[['Infected','Treated'], ['qMargin']], node_size = 4)
    ani.save(f'{sim_name}.mp4', writer=writer)


def convert_video(sim_name): 
    ff = ffmpy.FFmpeg(
        inputs = {f"{sim_name}.mp4" : None},
        outputs = {f"{sim_name}.gif" : None}
    )
    ff.run()


def main():
    
    parser = argparse.ArgumentParser(
        description=''
    )
    parser.add_argument('sim_name', type=str, nargs='?')
    parser.add_argument('sq_rate', type=float, nargs='?', default=0.05)
    parser.add_argument('qs_rate', type=float, nargs='?', default=0.01)
    parser.add_argument('it_rate', type=float, nargs='?', default=0.1)
    parser.add_argument('si_rate', type=float, nargs='?', default=0.5)
    parser.add_argument('population_size', type=int, nargs='?', default=250000)
    parser.add_argument('initial_infection_number', type=int, nargs='?', default=25)
    
    args = parser.parse_args()
    create_simulation(
        args.sim_name,
        args.sq_rate, 
        args.qs_rate, 
        args.it_rate,
        args.si_rate,
        args.population_size, 
        args.initial_infection_number
    )


if __name__ == "__main__":

    main()