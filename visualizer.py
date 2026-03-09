import matplotlib.pyplot as plt
import numpy as np

def radar_chart(features):

    labels = list(features.keys())
    values = list(features.values())

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)

    values += values[:1]
    angles = np.concatenate((angles, [angles[0]]))

    fig, ax = plt.subplots(subplot_kw={'polar': True})

    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.3)

    ax.set_thetagrids(angles[:-1] * 180/np.pi, labels)

    plt.show()