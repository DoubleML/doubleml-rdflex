import numpy as np

from matplotlib import pyplot as plt
from matplotlib import patches


def plot_shift(data, params, counterfactual=False, legend=False):
    # plot mean points
    fig = plt.figure()
    #plt.xlim(-1, 4)
    #plt.ylim(-1, 1)

    ax = plt.gca()
    #ax.set_aspect('equal', adjustable='box')

    # state
    color = plt.cm.rainbow(np.linspace(0, 1, params['n_obs']))
    for idx, (obs, c, treated, y0, y1) in enumerate(zip(data['state'], color, data['D'], data['Y0'], data['Y1'])):
        plt.scatter(obs[:,0], obs[:,1], color=c, label=f'{idx} {treated}|{y0:.4f}|{y1:.4f}|{y1-y0:.4f}')
    
    # target
    target_center = params['target_center']
    plt.scatter(target_center[0], target_center[1], color='black', marker='*')
    ellipse = patches.Ellipse(
        xy=target_center,
        width=params['target_a']*2,
        height=params['target_b']*2,
        edgecolor='black',
        fc='None', lw=2
    )
    ax.add_patch(ellipse)

    # treated state
    t_data = data['treated_state'] if counterfactual else data['final_state']
    for obs, c in zip(t_data, color):
        plt.scatter(obs[:,0], obs[:,1], color=c, marker='x')

    if legend:
        ax.legend(loc='lower left')


def plot_mean_shift(data, params, counterfactual=False, legend=False):    
    fig = plt.figure()
    plt.xlim(-1, 3)
    plt.ylim(-1, 1)
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    color = plt.cm.rainbow(np.linspace(0, 1, params['n_obs']))
    
    # state
    mean_point = np.mean(data['state'], axis=1)
    for idx, (mp, c, treated, y0, y1) in enumerate(zip(mean_point, color, data['D'], data['Y0'], data['Y1'])):
        plt.scatter(mp[0], mp[1], color=c, label=f'{idx} {treated} {y0:.4f}|{y1:.4f}|{y1-y0:.4f}')
    
    # target
    target_center = params['target_center']
    plt.scatter(target_center[0], target_center[1], color='black', marker='*')
    ellipse = patches.Ellipse(
        xy=target_center,
        width=params['target_a']*2,
        height=params['target_b']*2,
        edgecolor='black',
        fc='None', lw=2
    )
    ax.add_patch(ellipse)

    # treated state
    t_data = data['treated_state'] if counterfactual else data['final_state']
    mean_point = np.mean(t_data, axis=1)
    plt.scatter(mean_point[:,0], mean_point[:,1], c=color, marker='x')

    if legend:
        ax.legend(loc='lower left')