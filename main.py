import csv
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy

with open('data/sleeps.csv', 'r') as csvfile:
    sleeps = csv.reader(csvfile, delimiter=',', quotechar='|')
    next(sleeps, None)
    sleeps = [sleep for sleep in sleeps]

with open('data/feeds.csv', 'r') as csvfile:
    feeds = csv.reader(csvfile, delimiter=',', quotechar='|')
    next(feeds, None)
    feeds = [feed for feed in feeds]

with open('data/excretions.csv', 'r') as csvfile:
    poos = csv.reader(csvfile, delimiter=',', quotechar='|')
    next(poos, None)
    poos = [poo for poo in poos]

# Feeds
# id, Start Time, End Time, Feed Type, Quantity (oz), Quantity (ml or g), Notes, Duration (Minutes), Food Type, Unit, Bottle Type

# Sleeps
# id, Start Time, End Time, Notes, Approximate Duration (Minutes)

# Poos
# id, Time, Type, Notes

# Parse Sleeps
nsleeps = len(sleeps)
sleep_array = numpy.zeros(shape=[nsleeps,2], dtype=int)
i = 0
for sleep in sleeps:
    if len(sleep[2]) > 0:
        start = int(datetime.strptime(sleep[1], '%H:%M:%S %m-%d-%Y').strftime('%s'))
        end = int(datetime.strptime(sleep[2], '%H:%M:%S %m-%d-%Y').strftime('%s'))
        sleep_array[i] = [start, end]
        i += 1
    else:
        print('WARNING: Sleep Skipped!')

sleep_array = sleep_array[1:i, :]
sleep_lens = sleep_array[:, 1] - sleep_array[:, 0]

# Parse Feeds
feed_array = numpy.zeros(shape=[len(feeds),2], dtype=int)
i = 0
for feed in feeds:
    if len(feed[2]) > 0:
        start = int(datetime.strptime(feed[1], '%H:%M:%S %m-%d-%Y').strftime('%s'))
        end = int(datetime.strptime(feed[2], '%H:%M:%S %m-%d-%Y').strftime('%s'))
        feed_array[i] = [start, end]
        i += 1

feed_array = feed_array[1:i, :]
feed_lens = feed_array[:, 1] - feed_array[:, 0]

# Parse Excretions
poo_array = [int(datetime.strptime(poo[1], '%H:%M:%S %m-%d-%Y').strftime('%s')) for poo in poos]

feed_lens = feed_array[:, 1] - feed_array[:, 0]

# setup time intervals
one_minute = 60
one_hour = 60*one_minute
one_day = 24*one_hour
day_interval = 1

# adjust zero
zeroval = numpy.min(numpy.append(feed_array, sleep_array))
maxval = numpy.max(numpy.append(feed_array, sleep_array))

# start time on chosen hour
start_hour_of_day = 7
min_time = datetime.fromtimestamp(zeroval)
min_time_in_second_of_day = min_time.hour*one_hour + min_time.minute*one_minute + min_time.second
selected_start_time = start_hour_of_day*one_hour
zeroval = zeroval - min_time_in_second_of_day + selected_start_time

# adjust data based on zeroval
feed_array = feed_array - zeroval
sleep_array = sleep_array - zeroval
poo_array = poo_array - zeroval

# what is the actual minimum value now?
minval = numpy.min(numpy.append(feed_array, sleep_array))

# reverse arrays
feed_array = feed_array[-1:0:-1]
sleep_array = sleep_array[-1:0:-1]
poo_array = poo_array[-1:0:-1]

figure = plt.figure()
ax = figure.add_subplot(111, aspect='equal')


def plot_rect(info, color):
    start_hour = info[0]/one_hour
    duration_hours = (info[1] - info[0])/one_hour

    day = numpy.floor(start_hour / 24 ) * day_interval

    # adjust start_hour based on 24 hour period
    start_hour = start_hour - day*24
    end_hour = start_hour + duration_hours

    # check that starting before the hour doesn't end after hour
    if end_hour > 24:
        do_plot_rect(day, start_hour, 24 - start_hour, color)
        do_plot_rect(day + 1, 0, end_hour - 24, color)
    else:
        do_plot_rect(day, start_hour, duration_hours, color)


def do_plot_rect(day, start_hour, duration_hours, color):
    x = start_hour
    y = day*day_interval
    width = duration_hours
    height = day_interval

    patch = patches.Rectangle(
            (x, y),
            width,
            height )

    patch.set_color(color)

    ax.add_patch(patch)

    # line end rect
    if False:
        end_rect = x + width
        plt.plot([end_rect, end_rect], [y, y + 1], color=line_color, linewidth = line_width)
        plt.plot([x, x], [y, y + 1], color=line_color, linewidth = line_width)


ndays = numpy.round((maxval - zeroval)/one_day)

awake_color = '#028482'
feed_color = '#B76EB8'
sleep_color = '#7ABA7A'
line_color = 'white'
poo_color = 'black'
line_width = 2

# background patch
patch = patches.Rectangle(
    (0, 0),
    24,
    ndays + 1 )
patch.set_color(awake_color)
ax.add_patch(patch)

# background patch cutout
cutout_length = (min_time_in_second_of_day - selected_start_time)/one_hour
patch = patches.Rectangle(
    (-1, 0),
    cutout_length,
    1)
patch.set_color('white')
ax.add_patch(patch)

for feed in feed_array:
    plot_rect(feed, feed_color)

for sleep in sleep_array:
    plot_rect(sleep, sleep_color)

for poo in poo_array:
    plot_rect([poo, poo+10], poo_color)

# outline
if False:
    plt.plot([0, 0], [0,ndays], color=line_color, linewidth=line_width)
    plt.plot([24, 24], [0,ndays], color=line_color, linewidth=line_width)
    plt.plot([0, 24], [0, 0], color=line_color, linewidth=line_width)
    plt.plot([0, 24], [ndays, ndays], color=line_color, linewidth=line_width)

# daylines
if True:
    for day in numpy.arange(ndays+1):
        line, = plt.plot([0, 24], [day,day], color=line_color, linewidth=line_width)

# hide spines
if True:
    for key in ax.spines:
        ax.spines[key].set_visible(False)

    ax.axes.set_xticks([])
    ax.axes.set_yticks([])

# add day labels
if True:
    for day in range(int(ndays)):
        plt.text(-5, day, f'{day}  ')

# add hour lines
if True:
    for hour in range(24):
        plt.plot([hour,hour],[0,ndays+1],color='black')
        plt.text(hour-0.5, -1, f'{hour + 7}')

# middle line
plt.plot([12,12],[0,ndays+1],color='white',linewidth=1.0)


#ax.set_xlim([0, 24])
ax.autoscale_view()
plt.show()
plt.savefig('plot_figure.png')
print('hey')
