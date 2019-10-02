import os
import json 
import math
import csv
import matplotlib.pyplot as plt

def create_csv_file(directory, boundaries):
    """
    Create csv file from json files
    INPUT: directory containing json files, boolean denoting boundaries
    """
    N_data = {}
    for file in os.listdir(directory):
        if file.endswith('.json'):
            try:
                with open(os.path.join(directory, file), 'r') as handle:
                    parsed = json.load(handle)

                    try:
                        N = parsed['Cycles']
                    except KeyError:
                        N = parsed['Rounds']
                    L = parsed['L']
                    p = parsed['p']
                    trials = parsed['Trials']
                    limit = parsed['Timeout']
                    if boundaries: 
                        frequency = parsed['Sweep limit']
                        schedule = parsed['Sweep schedule']
                    fails = trials - parsed['Successes']
                    timeouts = trials - parsed['Clear syndromes']
                    runtime = parsed['Job RunTime (s)']

                    if N not in N_data:
                        N_data[N] = {}
                    if L not in N_data[N]:
                        N_data[N][L] = {}
                    if p not in N_data[N][L]:
                        N_data[N][L][p] = {}
                        N_data[N][L][p]['fails'] = fails
                        N_data[N][L][p]['timeouts'] = timeouts
                        N_data[N][L][p]['trials'] = trials
                        N_data[N][L][p]['max runtime'] = runtime
                        N_data[N][L][p]['total runtime'] = runtime
                        N_data[N][L][p]['limit'] = limit
                        if boundaries:
                            N_data[N][L][p]['schedule'] = schedule
                            N_data[N][L][p]['frequency'] = frequency
                    else:
                        N_data[N][L][p]['fails'] += fails
                        N_data[N][L][p]['timeouts'] += timeouts
                        N_data[N][L][p]['trials'] += trials
                        N_data[N][L][p]['total runtime'] += runtime
                        if runtime > N_data[N][L][p]['max runtime']:
                            N_data[N][L][p]['max runtime'] = runtime
            
            except ValueError:
                print(file)

    filename = directory + '_data.csv'
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        if boundaries:
            writer.writerow(['N', 'L', 'p', 'pfail', 'err', 'trials', 'fails', 'timeouts', 
                            'timeout %', 'limit', 'schedule', 'frequency', 'max runtime', 'total runtime'])
        else:
            writer.writerow(['N', 'L', 'p', 'pfail', 'err', 'trials', 'fails', 'timeouts', 
                            'timeout %', 'limit', 'max runtime', 'total runtime'])
         
        for N in N_data.keys():
            for L in N_data[N].keys():
                for p in N_data[N][L].keys():

                    fails = N_data[N][L][p]['fails']
                    trials = N_data[N][L][p]['trials']
                    timeouts = N_data[N][L][p]['timeouts']

                    pfail = fails / trials
                    if timeouts == 0:
                        timeout_pc = 0
                    else:
                        timeout_pc = timeouts / fails
                    err = math.sqrt((pfail * (1 - pfail)) / trials)

                    if boundaries:
                        writer.writerow([N, L, p, pfail, err, 
                                        N_data[N][L][p]['trials'],
                                        N_data[N][L][p]['fails'],
                                        N_data[N][L][p]['timeouts'],
                                        timeout_pc,
                                        N_data[N][L][p]['limit'],
                                        N_data[N][L][p]['schedule'],
                                        N_data[N][L][p]['frequency'],
                                        N_data[N][L][p]['max runtime'],
                                        N_data[N][L][p]['total runtime']])      
                    else:
                        writer.writerow([N, L, p, pfail, err, 
                                        N_data[N][L][p]['trials'],
                                        N_data[N][L][p]['fails'],
                                        N_data[N][L][p]['timeouts'],
                                        timeout_pc,
                                        N_data[N][L][p]['limit'],
                                        N_data[N][L][p]['max runtime'],
                                        N_data[N][L][p]['total runtime']])   
                
                
def plot_single(df, N, Ls, title):
    """
    Plot one threshold graph
    INTPUT: dataframe, cycle number N, list of Ls, title string
    """
    if N == -1:
        df_N = df
    else:
        df_N = df[(df['N'] == N)]
    for L in Ls:
        df_L = df_N[(df_N['L'] == L)]
        plt.errorbar('p', 'pfail', 'err', data=df_L, fmt='--o', markersize=8, label='L = %i' %L)
        ax = plt.gca()
        ax.set_ylabel('pL')
        ax.set_xlabel('p')
        ax.set_yscale('log')
        ax.legend(loc=4)
        plt.grid(True, 'both', 'both')
        ax.set_title(title)

def plot_double(dfs, Ls, titles, size):
    """
    Plot two threshold graphs side by side
    INTPUT: list of dataframes, list of Ls, list of titles, plot size
    """
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=size)
    i = 0
    for df in dfs:
        plt.sca(axes[i])
        for L in Ls:
            df_L = df[(df['L'] == L)]
            plt.errorbar('p', 'pfail', 'err', data=df_L, fmt='--o', markersize=8, label='L = %i' %L)
        ax = plt.gca()
        if i == 0:
            ax.set_ylabel('pL')
        ax.set_xlabel('p')
        ax.set_yscale('log')
        ax.legend(loc=4)
        plt.grid(True, 'both', 'both')
        ax.set_title(titles[i])
        i += 1

def plot_four(dfs, Ls, titles, size):
    """
    Plot four threshold graphs in tableaux
    INPUT: list of dataframes, list of Ls, list of titles, plot size
    """
    coord_list = [(0, 0), (0, 1), (1, 0), (1, 1)]
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=size)
    i = 0
    for df in dfs:
        plt.sca(axes[coord_list[i][0], coord_list[i][1]])
        for L in Ls:
            df_L = df[(df['L'] == L)]
            plt.errorbar('p', 'pfail', 'err', data=df_L, fmt='--o', markersize=8, label='L = %i' %L)
        ax = plt.gca()
        if i % 2 == 0:
            ax.set_ylabel('pL')
        if i > 1:
            ax.set_xlabel('p')
        ax.set_yscale('log')
        ax.legend(loc=4)
        plt.grid(True, 'both', 'both')
        ax.set_title(titles[i])
        i += 1



