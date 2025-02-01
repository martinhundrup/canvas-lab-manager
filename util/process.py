import pandas
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import time
import pathlib
import seaborn as sns
import urllib.request

import pandas as pd
import networkx as nx
import statistics

from math import sqrt, ceil

def save_websites(moss_output: pathlib.Path, save_dir: pathlib.Path) -> None:
    # Load all text files
    for text_file in moss_output.iterdir():
        # Load text
        moss_results = open(text_file.resolve(), 'r')
        moss_lines = moss_results.read().split('\n')
        print("moss results:")
        print(moss_results)
        # Get all urls
        url = None
        for line in moss_lines:
            print('line:' + line)
            if 'http' in line:
                url = line

        # Check if webpage already saved
        if (save_dir / (text_file.stem + '.html')).is_file():
            continue
        else:
            print('Saving: {pa} at {html}'.format(pa=text_file.stem, html=url))
            urllib.request.urlretrieve(url, save_dir / (text_file.stem + '.html'))
    return


def get_results(results_dir: pathlib.Path) -> dict:
    results = dict()

    for assignment in results_dir.iterdir():
        if '.html' not in assignment.name:
            continue

        results[assignment.stem] = list()

        with open(assignment) as fp:
            soup = BeautifulSoup(fp, 'html.parser')

        matched_lines = list()
        for ind, lines in enumerate(soup.find_all('td')):
            if ind % 3 == 2:
                matched_lines.append(int(lines.contents[0][0:-1]))

        links = list()
        urls = list()
        for link in soup.find_all('a')[6:]:
            links.append(link.string)
            urls.append(link['href'])

        for ind in range(int(len(links) / 2)):
            name_1 = links[ind*2].split(' ')[0]
            name_2 = links[ind*2+1].split(' ')[0]

            # **Fix: Extract TA & Student Names Correctly (Shift Right)**
            path_parts_1 = pathlib.Path(name_1).parts
            path_parts_2 = pathlib.Path(name_2).parts

            # Extracting TA & student names (moving one more level right)
            if len(path_parts_1) >= 2:
                ta_1, student_1 = path_parts_1[-2], path_parts_1[-1]
            else:
                ta_1, student_1 = "UNKNOWN_TA", "UNKNOWN_STUDENT"

            if len(path_parts_2) >= 2:
                ta_2, student_2 = path_parts_2[-2], path_parts_2[-1]
            else:
                ta_2, student_2 = "UNKNOWN_TA", "UNKNOWN_STUDENT"

            percent_1 = int(links[ind*2].split('%')[0].split('(')[1])
            percent_2 = int(links[ind*2+1].split('%')[0].split('(')[1])
            lines_shared = matched_lines[ind]
            url = urls[ind*2]

            results[assignment.stem].append({
                'PA': assignment.stem,
                'TA 1': ta_1, 'TA 2': ta_2,
                'student 1': student_1, 'student 2': student_2,
                'percent_1': percent_1, 'percent_2': percent_2,
                'lines_matched': lines_shared, 'url': url
            })

        results[assignment.stem] = pd.DataFrame(results[assignment.stem])

    return results



def plot_histograms(class_name: pathlib.Path, results: dict) -> None:
    plots_dir = class_name / 'plots'
    plots_dir.mkdir(exist_ok=True, parents=True)

    fig_size = ceil(sqrt(len(results.keys())))
    fig, ax = plt.subplots(nrows=fig_size, ncols=fig_size)

    for a_ind, assignment in enumerate(sorted(results.keys())):
        x = int(a_ind / fig_size)
        y = a_ind % fig_size

        mean = results[assignment][['percent_1', 'percent_2']].max(axis=1).mean()
        std = results[assignment][['percent_1', 'percent_2']].max(axis=1).std()
        if fig_size == 1:
            ax.hist(results[assignment][['percent_1', 'percent_2']].max(axis=1), bins=20, range=(0, 100))
            ax.axvline(min(mean + 1 * std, 80), color='r')
            ax.set_xlabel('Percent Same')
            ax.set_ylabel('Number of Students')
            ax.set_title(assignment)
        else:
            ax[x][y].hist(results[assignment][['percent_1', 'percent_2']].max(axis=1), bins=20, range=(0, 100))
            ax[x][y].axvline(mean + 1 * std, color='r')
            ax[x][y].set_xlabel('Percent Same')
            ax[x][y].set_ylabel('Number of Students')
            ax[x][y].set_title(assignment)

    # Set title
    fig.suptitle(class_name.parent.name)

    # Make everything fit
    plt.tight_layout()

    # Save plots
    plt.savefig(plots_dir / 'histogram.png',  dpi=1000)

    # Show the plot
    # plt.show()
    return None


def plot_connectedness(save_dir: pathlib.Path, results: dict) -> None:
    # Create sub dir for plots
    plots_dir = save_dir / 'plots'
    plots_dir.mkdir(exist_ok=True, parents=True)

    # Figure parameters
    plt.figure(figsize=(9, 9), dpi=500)

    for assignment in sorted(results.keys()):
        G = nx.Graph()
        mean = results[assignment]['percent_1'].mean()
        std = results[assignment]['percent_1'].std()
        for index, row in results[assignment].iterrows():
            if max(row['percent_1'], row['percent_2']) < min(mean + 1 * std, 80):
                continue
            G.add_edge(row['student 1'], row['student 2'], weight=max(row['percent_1'], row['percent_2'])/300, color='r')

        edges = G.edges()
        colors = [G[u][v]['color'] for u, v in edges]
        nx.draw(G, with_labels=True, font_size=4, edge_color=colors)
        plt.savefig(plots_dir / (assignment + '.png'), dpi=500)
        plt.clf()

    return None


def save_to_csv(save_dir: pathlib.Path, results: dict) -> None:
    # Check frequency by using standard deviation
    students = dict()
    for assignment in sorted(results.keys()):
        mean = results[assignment][['percent_1', 'percent_2']].max(axis=1).mean()
        std = results[assignment][['percent_1', 'percent_2']].max(axis=1).std()

        for index, row in results[assignment].iterrows():
            val_1 = (mean - row['percent_1']) / std
            if row['student 1'] not in students:
                students[row['student 1']] = val_1
            else:
                students[row['student 1']] += val_1

            val_2 = (mean - row['percent_2']) / std
            if row['student 2'] not in students:
                students[row['student 2']] = val_2
            else:
                students[row['student 2']] += val_2

    # Caluclate std of stds
    vals = sorted(students.values())
    std = statistics.pstdev(vals)
    mean = statistics.mean(vals)

    # Put in new values
    for key in students:
        students[key] = (students[key]-mean) / std

    # Format and save to spreadsheet
    all_data = None
    for assignment in sorted(results.keys()):
        # Add in additional columns for spreadsheet
        results[assignment]['percent_same'] = results[assignment][["percent_1", "percent_2"]].max(axis=1)
        results[assignment]['TA Confidence (1-5)'] = ''
        results[assignment]['HEAD TA Confidence (1-5)'] = ''

        # Exclude results
        p_mean = results[assignment][['percent_1', 'percent_2']].max(axis=1).mean()
        p_std = results[assignment][['percent_1', 'percent_2']].max(axis=1).std()
        results[assignment] = results[assignment][(results[assignment]['percent_1'] > p_mean + 1 * p_std) |
                                                  (results[assignment]['percent_2'] > p_mean + 1 * p_std) |
                                                  (results[assignment]['percent_1'] > 80) |
                                                  (results[assignment]['percent_2'] > 80) |
                                                  (results[assignment].index < 20)]

        # Add PA to total sheet
        if all_data is None:
            all_data = results[assignment]
        else:
            all_data = pd.concat([all_data, results[assignment]])

    # Save all data to excel
    all_data.to_excel(save_dir / (str(save_dir.parent.name) + '.xlsx'), sheet_name=save_dir.parent.name, index=False,
                      columns=['PA', 'TA 1', 'TA 2', 'student 1', 'student 2', 'percent_same',
                               'lines_matched', 'TA Confidence (1-5)', 'HEAD TA Confidence (1-5)', 'url'])
    return


def process_moss(course: pathlib.Path):
    results_dir = 'plagiarism'

    # Create results dir if not exist
    (course / results_dir).mkdir(exist_ok=True, parents=True)

    # Check and save moss results pages
    save_websites(course / 'moss_output', course / results_dir)

    # Perform operations on saved results
    results = get_results(course / results_dir)

    # Plot histograms
    plot_histograms(course / results_dir, results)

    # Plot network graph
    plot_connectedness(course / results_dir, results)

    # Save results to csv
    save_to_csv(course / results_dir, results)

    return
