import pandas as pd
import pathlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def plot_grade(course_dir: pathlib.Path, list_of_assignments: list) -> None:
    # Load TA list
    ta_list = pd.read_excel(course_dir / 'ta_list.xlsx')

    # Clear, Load, Subset df based on assignments and section name
    df = None
    df = pd.read_excel(course_dir / 'grade_book.xlsx')
    df = df[['Section'] + list_of_assignments]

    # If the TA has graded nothing in a column, but students still have zeros given (lates)
    # Then discount the entire column
    for column_name in df.columns:
        if df[column_name].replace(np.nan, 0).sum() == 0:
            df[column_name] = df[column_name].replace(0, np.nan)

    # Count
    df = df.groupby("Section").apply(lambda x: (1 - x.isna().mean()) * 100)

    # Remove excess key column
    df = df.iloc[:, 1:]

    # Plot as heatmap
    sns.heatmap(df, xticklabels=df.columns, yticklabels=ta_list['Name'].tolist(), cmap='mako')
    plt.ylabel('')
    plt.title(course_dir.name + ' - %graded')
    plt.tight_layout()
    plt.savefig(course_dir / 'percent_graded.png', dpi=300)
    plt.clf()

    return
