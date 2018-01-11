import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import time
import datetime
import config

#style.use("ggplot")

fig = plt.figure()
fig.patch.set_facecolor('black')
ax1 = fig.add_subplot(1, 1, 1)


def animate(i):
    pullData = open("twitter-live-out.txt", "r").read()
    lines = pullData.split('\n')

    xar1 = []
    yar1 = []
    xar2 = []
    yar2 = []
    x1 = x2 = y1 = y2 = 0

    for l in lines[-500:]:
        if l:
            sVal = l.split(',')
            v1 = float(sVal[0])
            v2 = float(sVal[1])

            # Topic1
            x1 += 1
            y1 += v1

            # Topic2
            x2 += 1
            y2 += v2

            xar1.append(x1)
            yar1.append(y1)

            xar2.append(x2)
            yar2.append(y2)

    ax1.clear()
    ax1.axhline(linewidth=2, color='yellow')
    ax1.plot(xar1, yar1, label=config.topic1)
    ax1.plot(xar2, yar2, label=config.topic2)

    plt.xlabel("Last 500 tweets", fontsize=12)
    plt.ylabel("Sentiment Value", fontsize=12)
    plt.title(config.theme)
    plt.legend(loc='upper left')

    plt.style.use("dark_background")


ani = animation.FuncAnimation(fig, animate, interval=2000)

plt.show()
