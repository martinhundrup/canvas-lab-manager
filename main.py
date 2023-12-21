import pathlib

from canvasapi import Canvas

from util.gui import GuiWindow
from util.gui import BetterConfig
from util.moss import *
from util.api import API
from util.process import *
from util.plot_grade import plot_grade
from util.plot_late import plot_late

from tkinter import filedialog
import tkinter as tk


def main():
    # Create gui window
    gui = GuiWindow()

    # Load config for previous runs
    config = BetterConfig('user_settings.ini')

    # Read in url
    saved_url = config.get('url', '')

    # Get user credentials here
    canvas_url, canvas_token = gui.get_user_credentials(['Enter Canvas url', 'Enter Canvas Token (not saved)'],
                                                        [saved_url, ''])

    # Save url
    config.set('url', canvas_url)

    '''
    # Get user save dir
    if config.get('save_path', '') == '':
        tk.Tk().withdraw()  # prevents an empty tkinter window from appearing
        folder_path = filedialog.askdirectory()
        config.set('save_path', folder_path)
    '''

    # Initialize a new API object
    api = API(canvas_url, canvas_token)

    # Get username
    canvas_user_name = api.get_current_user_name()

    # Get latest courses only
    latest_course_id = -1
    courses = dict()
    term_name = str()

    # Iterate through courses
    for i in api.get_courses():
        # Check if new enrollment term is found
        # Clear previous courses if so
        if i.enrollment_term_id > latest_course_id:
            latest_course_id = i.enrollment_term_id
            courses = dict()
            term_name = i.name

        # Check if course is in latest term
        if i.enrollment_term_id != latest_course_id:
            continue

        # Append courses to dict
        if i.course_code not in courses:
            courses[i.course_code] = list()
        courses[i.course_code].append(i.id)

    # create term name from course title
    term_name = '_'.join(reversed(term_name.split('-')[0:2]))

    # Update title to show current token holder
    gui.title('Canvas Lab Manager - {name}'.format(name=canvas_user_name))

    # Get which course to manage
    course = gui.get_course_selection(courses)
    api.set_current_course(course, courses[course])

    # Create course dir
    course_dir = pathlib.Path('terms') / term_name / course
    course_dir.mkdir(exist_ok=True, parents=True)
    api.set_course_dir(course_dir)

    # Run actions
    while True:
        # Get selected action in string form
        selected_action = gui.get_action_selection()

        if selected_action == 'exit':
            break
        elif selected_action == 'create_gradebook':
            gui.set_progress_bar(0)
            api.download_information(gui=gui)
            gui.set_progress_bar(0, reset=True)
        elif selected_action == 'switch_course':
            course = gui.get_course_selection(courses)
            api.set_current_course(course, courses[course])
        elif selected_action == 'download_submissions':
            list_of_assignments = api.get_assignments()
            gui.set_progress_bar(0)
            selected_assignments = gui.get_assignment_selection(list_of_assignments)
            api.download_information(download_student_code=True, assignments_list=selected_assignments, gui=gui)
            gui.set_progress_bar(0, reset=True)
        elif selected_action == 'run_moss':
            list_of_assignments = list()
            for assignment in (course_dir / 'assignments').iterdir():
                list_of_assignments.append(assignment.name)
                list_of_assignments = list(sorted(list_of_assignments))
            selected_assignments = gui.get_assignment_selection(list_of_assignments)
            run_moss(course_dir, selected_assignments, 'cc')
        elif selected_action == 'generate_cheating_spreadsheet':
            process_moss(course_dir)
        elif selected_action == 'grading_status':
            plot_grade(course_dir, api.get_assignments())
        elif selected_action == 'late_status':
            plot_late(course_dir, api.get_assignments())
        else:
            print('Selected Action is not yet implemented!!')

    # Destroy gui window at end
    gui.destroy()

    return


if __name__ == '__main__':
    main()
