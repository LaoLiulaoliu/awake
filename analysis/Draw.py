#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

plt.style.use('ggplot')
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


class Draw(object):
    def draw_scatter(self, data, x, y, color=None):
        plt.figure(figsize=(20, 8))
        if color is None:
            plt.scatter(data[x], data[y])
        else:
            plt.scatter(data[x], data[y], c=data[color])
        plt.title(x + '->' + y + ' color:' + str(color))
        plt.xlabel(x)
        plt.ylabel(y)
        plt.colorbar()
        plt.show()

    def draw_scatter_real_pred(self, real, pred, color=None):
        plt.figure(figsize=(20, 8))
        plt.scatter(real, pred, c=color)
        plt.plot(real, real, color='red')
        plt.title('real$pred')
        plt.xlabel('real')
        plt.ylabel('pred')
        plt.colorbar()
        plt.show()

    def draw_scatter_real_pred_withX1(self, data, x1, y, pred):
        plt.figure(figsize=(20, 8))
        plt.scatter(data[x1], data[y])
        plt.plot(data[x1], pred, color='red')
        plt.title(x1 + '&' + y + '&pred')
        plt.xlabel(x1)
        plt.ylabel(y)
        plt.colorbar()
        plt.show()

    def draw_hist(self, x):
        plt.figure(figsize=(20, 8))
        plt.hist(x)
        plt.title('bar')
        plt.xlabel('x')
        plt.ylabel('freq')
        plt.show()

    def draw_hist_1(self, data, cols):
        for col in cols:
            sns.distplot(data[col])
            plt.show()

    def draw_plot_data_xy(self, data, x, y, title='plot'):
        plt.figure(figsize=(20, 15))
        plt.xticks(range(len(data[x])), data[x])
        plt.plot(data[y], color='blue', label='actual')
        plt.legend()
        plt.title(title)
        plt.xlabel('time')
        plt.ylabel('value')
        plt.show()
        plt.close()

    def draw_plot_xy(self, x, y, title='plot'):
        plt.figure(figsize=(20, 15))
        ax = plt.subplot(1, 1, 1)

        xticks = list(range(0, len(x), 20))
        xlabels = [x[i] for i in xticks]
        ax.set_xticks(xticks)
        ax.set_xticklabels(xlabels, rotation=40)

        ax.plot(y, color='blue', label='actual')

        plt.legend()
        plt.title(title)
        plt.xlabel('time')
        plt.ylabel('value')
        # plt.show()
        plt.savefig(title)
        plt.close()

    def draw_plot(self, real, pred, title='plot'):
        plt.figure(figsize=(20, 8))
        plt.plot(np.arange(len(real)), real, color='blue', label='actual')
        plt.plot(np.arange(len(pred)), pred, color='red', label='predict')
        plt.legend()
        plt.title(title)
        plt.xlabel('time')
        plt.ylabel('value')
        plt.show()

    def draw_plot_multiply(self, data, x1, x2, x3):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        fig, ax1 = plt.subplots(figsize=(13, 5), facecolor='white')
        x = range(len(data))
        ax1.scatter(x, data[x1], s=2, c='r')
        ax1.set_ylabel(x1, color='r')
        ax2 = ax1.twinx()
        ax2.scatter(x, data[x2], s=2, c='g')
        ax2.set_ylabel(x2, color='g')

        if x3 is not None:
            ax3 = ax1.twinx()
            ax3.scatter(x, data[x3], s=2, c='b')
            ax3.set_ylabel(x3, color='b')

        plt.legend()
        plt.show()

    def draw_compare_two(self, data, x, x1, x2):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        fig, ax1 = plt.subplots(figsize=(13, 5), facecolor='white')
        plt.xlabel(x)
        ax1.plot(data[x], data[x1], c='r')
        ax1.set_ylabel(x1, color='r')
        ax2 = ax1.twinx()
        ax2.plot(data[x], data[x2], c='g')
        ax2.set_ylabel(x2, color='g')

        plt.legend()
        plt.show()

    def draw_3d(self, x1, x2, y):
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure()
        ax = Axes3D(fig)
        ax.scatter(x1, x2, y)
        plt.show()

    def draw_compare3d(self, x1, x2, y1, y2):
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure()
        ax = Axes3D(fig)
        ax.scatter(x1, x2, y1)
        ax.scatter(x1, x2, y2)
        plt.show()

    def covariance_heatmap(self, data):
        fig, ax = plt.subplots(figsize=(20, 8))
        corr_mat = data.corr()
        sns.heatmap(corr_mat, vmax=0.8, square=True)
        plt.show()
