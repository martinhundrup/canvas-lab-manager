# Import the Canvas class
import copy
import pandas as pd
import pathlib
import shutil
import zipfile
import py7zr

from canvasapi import Canvas
from canvasapi.course import Course


# API Class for managing all API calls to canvas
class API:

    def __init__(self, canvas_url, canvas_token):
        # Store arguments
        self.canvas_url = canvas_url
        self.canvas_token = canvas_token

        # Create canvas object
        self.canvas = Canvas(self.canvas_url, self.canvas_token)

        # Other
        self.course_ids = None
        self.course_name = None
        self.course_dir = None

        return

    # Get current user, based on token access
    def get_current_user_name(self):
        return self.canvas.get_current_user().name

    # Get PaginatedList of courses (not fully loaded, needs to iterate through)
    def get_courses(self):
        return self.canvas.get_courses()

    # Set current course name and course id list (associated with name)
    def set_current_course(self, course_name: str, course_ids: list) -> None:
        self.course_name = course_name
        self.course_ids = course_ids
        return

    # Sets api wide directory for storing material
    def set_course_dir(self, course_dir: pathlib.Path) -> None:
        self.course_dir = course_dir
        return

    def download_information(self, download_student_code: bool = False,
                             assignments_list: list = None, gui=None) -> None:
        print("Course:", self.course_name)
        all_data = None
        all_tas = None

        # Iterate through all subsections of course
        for course_ind, course_id in enumerate(self.course_ids):
            print("\tCourse Section:", course_id)
            course = self.canvas.get_course(course_id)

            student_info = get_students_info(course)

            ta_info = get_section_graders(course)

            assignments = get_grade_book(course)

            if download_student_code:
                download_submissions(course, self.course_dir, student_info, ta_info, assignments_list,
                                     gui, 100 / len(self.course_ids))

            final_scores = get_cumulative_score(course)

            grade_book = pd.merge(student_info, assignments, on='ID')
            grade_book = pd.merge(grade_book, final_scores, on='ID')

            if all_data is None:
                all_data = grade_book
            else:
                all_data = pd.concat([all_data, grade_book], ignore_index=True)

            if all_tas is None:
                all_tas = ta_info
            else:
                all_tas = pd.concat([all_tas, ta_info], ignore_index=True)

            # Update gui
            if not download_student_code:
                gui.set_progress_bar(100 / len(self.course_ids))

        # Copy late data
        all_data_late = copy.deepcopy(all_data)

        # Remove late from column names
        for column_name in all_data.columns:
            if '-Late' in column_name:
                all_data = all_data.drop(column_name, axis=1)

        all_data.to_excel(self.course_dir / 'grade_book.xlsx')
        all_data_late.to_excel(self.course_dir / 'grade_book_late.xlsx')
        all_tas.to_excel(self.course_dir / 'ta_list.xlsx')
        return

    def get_assignments(self) -> list:
        # Get assignments from the first course in the list of course ids
        course_assignments = self.canvas.get_course(self.course_ids[0]).get_assignments()
        list_of_assignments = list()

        for course_assignment in course_assignments:
            list_of_assignments.append(course_assignment.name)

        return list_of_assignments


def get_students_info(course_instance: Course) -> pd.DataFrame:
    # Students to hold list for putting into pandas
    students = list()

    # Student type
    type_list = ['student']
    users = course_instance.get_users(enrollment_type=type_list)

    # Get information from all students
    for user in users:
        # Can use sortable_name if needed
        students.append({'Name': user.name,
                         'ID': user.id,
                         'SIS User ID': user.sis_user_id,
                         'SIS Login ID': user.login_id,
                         'Section': course_instance.name.split(' ')[0],
                         'Type': 'student'})

    return pd.DataFrame(students)


def get_grade_book(course_instance: Course) -> pd.DataFrame:
    course_assignments = course_instance.get_assignments()

    everything = dict()

    for course_assignment in course_assignments:
        for submission in course_assignment.get_submissions():
            if submission.user_id not in everything:
                everything[submission.user_id] = dict()

            everything[submission.user_id][course_assignment.name] = submission.score
            everything[submission.user_id][course_assignment.name + '-Late'] = submission.seconds_late

    # Transpose the spreadsheet
    section_grade_book = pd.DataFrame(everything).T

    # The index is now user ID
    section_grade_book = section_grade_book.reset_index()

    # Set column name to reflect above
    section_grade_book = section_grade_book.rename(columns={'index': 'ID'})

    return section_grade_book


def get_section_graders(course_instance: Course) -> pd.DataFrame:
    head_ta_list = ['Christopher Pereyda']
    tas = list()
    type_list = ['ta']
    teach_assistants = course_instance.get_users(enrollment_type=type_list)

    # Get information from all students
    for teach_assistant in teach_assistants:
        tas.append({'Name': teach_assistant.name,
                    'ID': teach_assistant.id,
                    'SIS User ID': teach_assistant.sis_user_id,
                    'SIS Login ID': teach_assistant.login_id,
                    'Section': course_instance.name.split(' ')[0],
                    'Type': 'TA'})

    tas = pd.DataFrame(tas)
    times = list()

    for section in course_instance.get_sections():
        for student in section.get_enrollments():
            if student.type != 'TaEnrollment':
                continue

            if student.user['name'] in head_ta_list:
                continue

            times.append({'Name': student.user['name'], 'total_activity_time': student.total_activity_time})

    times = pd.DataFrame(times)

    ta_info = pd.merge(tas, times, on='Name')

    ta_info = ta_info[ta_info['total_activity_time'] == ta_info['total_activity_time'].max()]

    return ta_info


def get_cumulative_score(course_instance: Course) -> pd.DataFrame:
    students = list()
    for section in course_instance.get_sections():
        for student in section.get_enrollments():
            if student.type != 'StudentEnrollment':
                continue
            students.append({'ID': student.user_id,
                             'current_score': student.grades['current_score'],
                             'final_score': student.grades['final_score']})

    return pd.DataFrame(students)


# Takes in file and makes it utf8 by default (so it can get processed in moss)
def convert_to_text(path: pathlib.Path) -> None:

    try:
        with open(path.resolve(), 'r', encoding='utf16') as f:
            text = f.read()

        # process Unicode text

        with open(path.resolve(), 'w', encoding='utf8') as f:
            f.write(text)

    except UnicodeError as e:
        pass

    return


def process_submission(code_dir: pathlib.Path, zip_type: bool = False, zip7_type: bool = False) -> None:
    if zip_type:
        # Extract out the zip code
        try:
            with zipfile.ZipFile(code_dir.with_suffix('.zip'), 'r') as zip_ref:
                zip_ref.extractall(code_dir)
        except zipfile.BadZipfile as e:
            print("Student {} failed to submit a valid zip!".format(code_dir.name))
        # Remove zipped download
        code_dir.with_suffix('.zip').unlink()

    elif zip7_type:
        try:
            with py7zr.SevenZipFile(code_dir.with_suffix('.7z'), mode='r') as z:
                z.extractall(code_dir)
        except zipfile.BadZipfile as e:
            print("Student {} failed to submit a valid zip!".format(code_dir.name))
        # Remove zipped download
        code_dir.with_suffix('.7z').unlink()

    # Check for empty archives
    if not code_dir.is_dir():
        return

    # Extract out one layer of zips if necessary
    for path in code_dir.rglob('*.zip'):
        # Some students submit dirs named '.zip' that aren't actually zips
        if zipfile.is_zipfile(path.resolve()):
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(str(path.resolve())[0:-4])

    # Create temp dir for storing code
    code_dir_tmp = pathlib.Path(str(code_dir.resolve()) + '-t')
    code_dir_tmp.mkdir(exist_ok=True)

    # Now everything is extracted, search for .c files and put in sub dir
    file_types = ['.c', '.cpp']

    for file_type in file_types:
        for path in code_dir.rglob('*' + file_type):
            # Remove hidden file submissions
            if '.' == path.name[0]:
                continue

            # Do not include CMake files
            if 'CMake' in path.name:
                continue

            # Case for students putting in PA1.c as a dir
            if path.is_dir():
                continue

            # Case for small corrupted files, 100 byte limit
            # TODO: might wanna make dynamic later
            if path.stat().st_size < 100:
                continue

            # Make sure file is text only
            convert_to_text(path)

            shutil.copy(path, code_dir_tmp)  # For Python 3.8+.

    # Remove base dir and switch tmp dir to primary dir
    shutil.rmtree(code_dir)
    code_dir_tmp.rename(str(code_dir_tmp.resolve())[0:-2])

    return


def download_submissions(course_instance: Course, course_dir: pathlib.Path,
                         student_info: pd.DataFrame, ta_info: pd.DataFrame, assignments_list: list, gui, step) -> None:

    course_assignments = course_instance.get_assignments()
    for course_assignment in course_assignments:
        if assignments_list is not None:
            if course_assignment.name not in assignments_list:
                continue

        print('\t\tDownloading:', course_assignment.name)

        for submission in course_assignment.get_submissions():
            # Check for a submission
            if len(submission.attachments) == 0:
                continue

            # Get TA name
            try:
                ta_name = ta_info['Name'].values[0]
            except Exception as e:
                # Ungraded assignment case
                ta_name = 'N/A'

            ta_name = ta_name.replace(' ', '_')

            # Get student name
            student_name = student_info['Name'][student_info['ID'] == submission.user_id].values[0].replace(' ', '_')

            # Setup file structure course / pa / ta / student / code
            code_dir = course_dir / 'assignments' / course_assignment.name / ta_name
            code_dir.mkdir(exist_ok=True, parents=True)

            # Skip if we already downloaded
            # TODO: let user overwrite and re-download (for now just del folders)
            if (code_dir / student_name).is_dir():
                continue

            # Grab student file name
            student_file_name = submission.attachments[-1].filename

            zip_type = False
            zip7_type = False

            if '.zip' == student_file_name[-4:]:
                # Download zip file
                submission.attachments[-1].download(code_dir / (student_name + '.zip'))
                zip_type = True

            elif '.7z' == student_file_name[-3:]:
                # Download 7zip file
                submission.attachments[-1].download(code_dir / (student_name + '.7z'))
                zip7_type = True

            else:
                # Make student dir
                student_code = code_dir / student_name
                student_code.mkdir(exist_ok=True)

                # Download normal file
                submission.attachments[-1].download(student_code / student_file_name)

                # Print notice to user
                print('Warning: Student {} did not submit a zip file!'.format(student_name))

            # Extract out code
            process_submission(code_dir / student_name, zip_type=zip_type, zip7_type=zip7_type)

        # Update gui
        gui.set_progress_bar(step / len(assignments_list))

    return
