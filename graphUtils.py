import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree

LABEL_COLOR = "#dddddd"
BUBBLE_COLOR = "#63d065"

xMax = 1
yMax = 1

def get_label_xy(tree, thresh, data, i):
    neighbors = tree.query_ball_point([data[i, 0], data[i, 1]], thresh)
    print neighbors

    if len(neighbors) == 1:
        xy = (-30, 30)
    else:

        print("To mean: " + str(data[:, :2][neighbors]))
        mean = np.mean(data[:, :2][neighbors], axis=0)

        print("Mean: " + str(mean))

        if mean[0] == data[i, 0] and mean[1] == data[i, 1]:
            if i < np.max(neighbors):
                xy = (-30, 30)
            else:
                xy = (30, -30)
        else:
            angle = np.arctan2(data[i, 1] - mean[1], data[i, 0] - mean[0])

            if angle > np.pi / 2:
                xy = (-30, 30)
            elif angle > 0:
                xy = (30, 30)
            elif angle > -np.pi / 2:
                xy = (30, -30)
            else:
                xy = (-30, -30)

        print xy
    return xy


def labeled_scatter_plot(data, labels, plt_in):

    # Get the max of each axis
    xMax = data[:, :2][:, 0].max()
    yMax = data[:, :2][:, 1].max()
    zMax = data[:, 2].max()

    # Plot bubbles in scatter
    plt_in.scatter(
        #data[:, 0], data[:, 1], marker = 'o', c = data[:, 2], s = data[:, 3]*1500,
        data[:, 0], data[:, 1], marker='o', c = BUBBLE_COLOR, s=1000*(data[:, 2]/float(zMax)),
        cmap = plt.get_cmap('Spectral'))

    # Get xyData points scaled to 1
    xData = data[:, :2][:, 0]/float(xMax)
    yData = data[:, :2][:, 1]/float(yMax)

    xyData = np.append([xData], [yData], axis=0)
    xyData = np.transpose(xyData)

    print "xyData:"
    print xMax
    print yMax
    print xyData


    tree = cKDTree(xyData[:, :2])
    thresh = 0.1

    for i in range(data.shape[0]):

        print ("\nLabel: " + labels[i] + ", " + str(i))
        xy = get_label_xy(tree, thresh, xyData, i)

        plt_in.annotate(
            labels[i],
            xy = data[i, :2], xytext = xy,
            textcoords = 'offset points', ha = 'center', va = 'center',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = LABEL_COLOR, alpha = 0.75),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
