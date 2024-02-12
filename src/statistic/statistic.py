import json
import matplotlib.pyplot as plt

OUTPUT_PATH = '../../output/PMCOA_out.json'


def draw(data, title):
    plt.hist(data, bins=30, color='blue', alpha=0.7)
    plt.title(title)
    plt.xlabel('Number')
    plt.ylabel('Frequency')
    plt.show()


num_sample = 0
num_no_caption = 0
num_figures = []
num_tables = []
num_figures_tables = []

with open(OUTPUT_PATH, 'r') as json_file:
    for line in json_file:
        data_dict = json.loads(line)

        if data_dict['num_figure'] + data_dict['num_table'] > 0:
            num_sample = num_sample + 1

        num_figures.append(data_dict['num_figure'])
        num_tables.append(data_dict['num_table'])
        num_figures_tables.append(data_dict['num_table+figure'])

        if data_dict['wo_caption']:
            num_no_caption = num_no_caption + 1

average_figure = round(sum(num_figures) / num_sample, 2)
average_table = round(sum(num_tables) / num_sample, 2)

print('Average Figures: {}'.format(average_figure))
print('Average Tables: {}'.format(average_table))
print('Average Tables + Figures: {}'.format(average_table + average_figure))
print('Sample Size: {}'.format(num_sample))
print('Sample Without Captions: {}'.format(num_no_caption))

draw(num_figures, 'num_figures')
draw(num_tables, 'num_tables')
draw(num_figures_tables, 'num_figures_tables')
