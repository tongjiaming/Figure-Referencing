import numpy as np
import matplotlib.pyplot as plt


def visualize(x, y1, y2, title='', x_label='', y_label='', y1_label='', y2_label=''):
    plt.plot(x, y1, color='blue', label=y1_label)
    plt.plot(x, y2, color='red', label=y2_label)

    plt.title(title)
    plt.xlabel(x_label)
    plt.xlabel(y_label)

    plt.savefig('tfidf.png')
    plt.show()


def find_threshold(data_path, evaluate_fun, num_thresholds=11):
    # try different threshold and draw a line chart
    thresholds = np.linspace(0, 1, num_thresholds)
    precisions = []
    recalls = []

    for threshold in thresholds:
        print('Working on threshold {}.'.format(threshold))
        _, precision, recall = evaluate_fun(data_path, threshold=threshold)

        # For rouge only, choose rouge2
        if isinstance(precision, list):
            precision = precision[1]
        if isinstance(recall, list):
            recall = recall[1]

        precisions.append(precision)
        recalls.append(recall)

    visualize(thresholds, precisions, recalls, x_label='threshold', y1_label='precisions', y2_label='recalls')
