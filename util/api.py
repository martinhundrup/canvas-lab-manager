# Import the Canvas class
import copy
import pandas as pd
import pathlib
import shutil
import zipfile
import py7zr
import re

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



def sanitize_path_component(component: str) -> str:
    """
    Sanitizes a file or directory name by removing or replacing problematic characters.
    """
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', component)

    # Ensure no control characters or leading/trailing whitespace
    sanitized = sanitized.strip()

    # Truncate overly long file names (limit to 255 characters)
    return sanitized[:255]


def process_submission(code_dir: pathlib.Path, zip_type: bool = False, zip7_type: bool = False) -> None:
    if zip_type:
        try:
            with zipfile.ZipFile(code_dir.with_suffix('.zip'), 'r') as zip_ref:
                for zipinfo in zip_ref.infolist():
                    # Sanitize file name
                    sanitized_name = sanitize_path_component(zipinfo.filename)

                    # Determine target path
                    target_path = code_dir / sanitized_name

                    # Handle path conflicts
                    if target_path.exists() and not target_path.is_dir():
                        print(f"Conflict detected for {target_path}. Renaming...")
                        target_path = target_path.with_name(target_path.stem + '_conflict')

                    # Ensure parent directories exist
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # Extract file
                    with open(target_path, 'wb') as f_out:
                        f_out.write(zip_ref.read(zipinfo))
        except zipfile.BadZipFile as e:
            print(f"Invalid ZIP file for student {code_dir.name}: {e}")
        finally:
            # Remove the original ZIP file
            code_dir.with_suffix('.zip').unlink(missing_ok=True)

    elif zip7_type:
        try:
            with py7zr.SevenZipFile(code_dir.with_suffix('.7z'), mode='r') as z:
                z.extractall(path=code_dir)
        except Exception as e:
            print(f"Invalid 7z file for student {code_dir.name}: {e}")
        finally:
            # Remove the original 7z file
            code_dir.with_suffix('.7z').unlink(missing_ok=True)

    # Check for empty directories
    if not code_dir.is_dir():
        print(f"Directory {code_dir} is missing or not created.")
        return

    # Extract nested ZIP files, if any
    for nested_zip in code_dir.rglob('*.zip'):
        if zipfile.is_zipfile(nested_zip):
            try:
                print(f"Processing nested ZIP: {nested_zip}")
                with zipfile.ZipFile(nested_zip, 'r') as zip_ref:
                    extract_target = nested_zip.parent / nested_zip.stem
                    extract_target.mkdir(exist_ok=True)
                    zip_ref.extractall(extract_target)
            except Exception as e:
                print(f"Error processing nested ZIP {nested_zip}: {e}")
            finally:
                # Remove the nested ZIP after extraction
                nested_zip.unlink(missing_ok=True)

    # Create a temporary directory for extracted code
    code_dir_tmp = pathlib.Path(str(code_dir.resolve()) + '-t')
    code_dir_tmp.mkdir(exist_ok=True)

    # Move valid code files (.c, .cpp) to the temporary directory
    file_types = ['.c', '.cpp']
    for file_type in file_types:
        for file_path in code_dir.rglob('*' + file_type):
            # Skip hidden files or invalid entries
            if file_path.name.startswith('.') or not file_path.is_file():
                continue

            # Skip very small or corrupted files
            if file_path.stat().st_size < 100:
                print(f"Skipping small or corrupted file: {file_path}")
                continue

            # Ensure the file is text format
            convert_to_text(file_path)

            # Copy valid files to the temp directory
            shutil.copy(file_path, code_dir_tmp)

    # Remove the original directory and rename the temp directory
    shutil.rmtree(code_dir)
    code_dir_tmp.rename(code_dir)

    print(f"Processing completed for: {code_dir}")

    return


def convert_to_text(path: pathlib.Path) -> None:
    """
    Converts a file to UTF-8 encoding if necessary to ensure compatibility.
    """
    try:
        with open(path, 'r', encoding='utf-16') as f_in:
            content = f_in.read()
        with open(path, 'w', encoding='utf-8') as f_out:
            f_out.write(content)
    except UnicodeError:
        print(f"File {path} is not in UTF-16 format or conversion failed. Skipping conversion.")


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
