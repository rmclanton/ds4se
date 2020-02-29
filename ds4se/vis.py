# AUTOGENERATED! DO NOT EDIT! File to edit: dev/10_vis.ipynb (unless otherwise specified).

__all__ = ['visualize_gt_ngt', 'visualize_events']

# Cell
# Imports
import matplotlib.pyplot as plt

# Cell
def visualize_gt_ngt(gt, ngt):
    plt.scatter(gt[0], gt[1], c='b')
    plt.scatter(ngt[0], ngt[1], c='r')
    plt.show()

# Cell
def visualize_events(events, color):
    plt.hlines(1,0,1)  # Draw a horizontal line
    plt.eventplot(events, orientation='horizontal', colors=color, alpha = 0.5)
    plt.show()