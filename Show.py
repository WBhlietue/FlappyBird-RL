import matplotlib.pyplot as plt
import numpy as np
import time
import csv

# 创建一个空图形
plt.ion()
fig, (ax1, ax2) = plt.subplots(2)
# fig, (ax1) = plt.subplots(1, figsize=(15, 2))

while True:
    file = open("reward.txt", "r")
    data = csv.reader(file, delimiter=",")
    x_values = []
    y_values = []
    z_values = []
    a = 0
    # 逐行读取数据
    for row in data:
        x_values.append(a)
        a += 1
        y_values.append(float(row[1]))
        z_values.append(float(row[2]))

    ax1.clear()
    ax1.plot(x_values, y_values, linestyle='-', marker='o', markersize=0.1)  # 使用 plot 函数绘制折线图
    ax1.set_title('Train Num')
    ax1.set_xlabel('Train Num')
    ax1.set_ylabel('Reward')

    ax2.clear()
    ax2.plot(z_values, y_values, linestyle='-', marker='o', markersize=1, color='red')  # 使用 plot 函数绘制折线图
    ax2.set_title('Epsilon')
    ax2.set_xlabel('Epsilon')
    ax2.set_ylabel('Reward')
    plt.subplots_adjust(hspace=1)

    plt.draw()
    plt.pause(1)  # 控制更新频率
    if not plt.fignum_exists(fig.number):
        break

