import pandas as pd
import pathlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def plot_late(course_dir: pathlib.Path, list_of_assignments: list) -> None:
    # Load TA list
    ta_list = pd.read_excel(course_dir / 'ta_list.xlsx')

    # Clear, Load, Subset df based on assignments and section name
    df = None
    df = pd.read_excel(course_dir / 'grade_book_late.xlsx')

    # Compute number of days late assignments
    data = dict()
    for index, row in df.iterrows():
        for assignment in list_of_assignments:
            ta_name = ta_list[ta_list['Section'] == row['Section']]['Name'].values[0]
            if ta_name not in data:
                data[ta_name] = [0] * 15

            weeks_late = row[assignment+'-Late'] / (60*60*24*7)
            if row[assignment] != 0 and weeks_late > 1:
                data[ta_name][int(weeks_late)] += 1

    data = pd.DataFrame(data).T
    sns.heatmap(data, cmap='mako_r')
    plt.title(course_dir.name + ' weeks late acceptance')
    plt.tight_layout()
    plt.savefig(course_dir / 'late_status.png', dpi=400)
    return
