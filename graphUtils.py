import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree

LABEL_COLOR = "#dddddd"
BUBBLE_COLOR = "#63d065"

xMax = 1
yMax = 1

def get_label_xy(xyData, i):

    tree = cKDTree(xyData)
    thresh = 0.15

    neighbors = tree.query_ball_point([xyData[i, 0], xyData[i, 1]], thresh)

    if len(neighbors) == 1:
        xy = (-30, 30)
    else:
        mean = np.mean(xyData[:, :2][neighbors], axis=0)

        if mean[0] == xyData[i, 0] and mean[1] == xyData[i, 1]:
            if i < np.max(neighbors):
                xy = (-30, 30)
            else:
                xy = (30, -30)
        else:
            angle = np.arctan2(xyData[i, 1] - mean[1], xyData[i, 0] - mean[0])

            if angle > np.pi / 2:
                xy = (-30, 30)
            elif angle > 0:
                xy = (30, 30)
            elif angle > -np.pi / 2:
                xy = (30, -30)
            else:
                xy = (-30, -30)

    return xy


def labeled_scatter_plot(data, labels, plt_in):

    # Get the max of each axis
    xMax = data[:, :2][:, 0].max()
    yMax = data[:, :2][:, 1].max()
    zMax = data[:, 2].max()

    xMin = data[:, :2][:, 0].min()
    yMin = data[:, :2][:, 1].min()
    zMin = data[:, 2].min()

    print("yMax = %s" % yMax)


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

    #xyData = np.append(xyData, [[45 / xMax, 3 / yMax]], axis=0)

    for i in range(data.shape[0]):
        xy = get_label_xy(xyData, i)
        r = plt_in.annotate(
            labels[i],
            xy = data[i, :2], xytext = xy,
            textcoords = 'offset points', ha = 'center', va = 'center',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = LABEL_COLOR, alpha = 0.75),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

        xy = np.array(xy) * [0.08*xMax/30.0, 0.12*yMax/30.0]
        xyLabel = data[i, :2] + xy
        xyLabelScaled1 = xyLabel * [1/xMax, 1/yMax]

        #plt_in.scatter(xyLabel[0], xyLabel[1], marker='o', c="red", s=1000,
         #   cmap=plt.get_cmap('Spectral'))

        xyData = np.append(xyData, [xyLabelScaled1], axis=0)

    if(xMin > 0):
        plt_in.xlim(xmin=0)
    else:
        plt_in.xlim(xmin = xMin * 1.2)
    plt_in.xlim(xmax=xMax * 1.2)

    if(yMin > 0):
        plt_in.ylim(ymin = 0)
    else:
        plt_in.ylim(ymin = yMin * 1.2)

    if(yMax > 0):
        plt_in.ylim(ymax = yMax*1.2)
    else:
        plt_in.ylim(ymax= yMax *(-1.2))

