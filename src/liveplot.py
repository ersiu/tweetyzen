import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import time
import datetime
import argparse
import configparser

def animate2(i):
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
    ax1.axhline(linewidth=2, color='black')
    ax1.plot(xar1, yar1, label=c_topic1, color='red')
    ax1.plot(xar2, yar2, label=c_topic2, color='blue')

    plt.xlabel("Last 500 tweets", fontsize=12)
    plt.ylabel("Sentiment Value", fontsize=12)
    plt.title(c_theme)
    plt.legend(loc='upper left')


def animate1(i):
    pullData = open(c_live_out_file, "r").read()
    lines = pullData.split('\n')

    xar = []
    yar = []
    x = 0
    y = 0

    for l in lines[-500:]:
        if l:
            sVal = l.split(',')
            v = float(sVal[0])
            x += 1
            y += v
            xar.append(x)
            yar.append(y)

    ax1.clear()
    ax1.axhline(linewidth=2, color='black')
    ax1.plot(xar, yar, label=c_topic1, color='red')

    plt.xlabel("Last 500 tweets", fontsize=12)
    plt.ylabel("Sentiment Value", fontsize=12)
    plt.title(c_theme)
    plt.legend(loc='upper left')

    # plt.style.use("dark_background")

#-------------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='zenliveplot.py')

parser.add_argument('-c','--config', help='provide config.ini file location', required=True)
parser.add_argument('-r','--reset', help='reset out file', required=False, action='store_true')
parser.add_argument('-t','--theme', help='set title', required=False)
parser.add_argument('-n','--ntopic', help='number of topic', required=False)

args = vars(parser.parse_args())

c_config_file = ''

if args['config']:
     c_config_file = args['config']
     print(">>>>> Load config file: ", c_config_file)

config = configparser.ConfigParser()
config.read(c_config_file)

c_live_out_file = config.get("general", "live_out_file")
if args['ntopic']:
    c_no_of_topic = int(args['ntopic'])
else:
    c_no_of_topic = int(config.get("topic", "no_of_topic"))

c_theme =''
if args['theme']:
	c_theme = args['theme']
	c_topic1 = c_theme
	print(">>>>> set theme: ", c_theme)
else:
	c_theme = config.get("topic", "theme")
	c_topic1 = config.get("topic", "topic1")

	print(">>>>> load theme: ", c_theme)

c_topic2 = config.get("topic", "topic2")

if args['reset']:
	open(c_live_out_file, 'w').close()
	print(">>>>> cleared file: ", c_live_out_file)


fig = plt.figure()
# fig.patch.set_facecolor('black')
ax1 = fig.add_subplot(1, 1, 1)

if c_no_of_topic == 1:
	ani = animation.FuncAnimation(fig, animate1, interval=2000)
	plt.show()
else:
	ani = animation.FuncAnimation(fig, animate2, interval=2000)
	plt.show()


# ani = animation.FuncAnimation(fig, animate1, interval=2000)

# plt.show()
