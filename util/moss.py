import pathlib
import pandas as pd
import stat
import subprocess


def run_moss(course_dir: pathlib.Path, assignments_list: list, language: str = 'cc') -> None:
    generate_moss(course_dir, assignments_list, language)
    subprocess.call(['sh', str((course_dir / 'run_moss.sh').relative_to('.'))])
    return


def generate_moss(course_dir: pathlib.Path, assignments_list: list, language: str = 'cc') -> None:
    # Get the absolute path to the `moss` script
    moss_path = (pathlib.Path(__file__).parent.parent / "moss").resolve()

    # Paths for MOSS command file and output directory
    moss_command_path = course_dir / 'run_moss.sh'
    moss_output_path = course_dir / 'moss_output'
    moss_output_path.mkdir(exist_ok=True, parents=True)

    # Path to student submissions
    class_code = course_dir / 'assignments'

    # Open file (w to overwrite and clean previous runs)
    with open(moss_command_path.relative_to('.'), 'w') as f_out:
        for assignment in assignments_list:
            # **Escape quotes and special characters in assignment & course names**
            assignment_safe = assignment.replace('"', '\\"').replace("'", "\\'")
            course_name_safe = course_dir.name.replace('"', '\\"').replace("'", "\\'")

            # **Use absolute path for `moss`**
            f_out.write(f'"{moss_path}" -d -l {language} -m 1000000 ')
            f_out.write(f'-c "{assignment_safe} in {course_name_safe}" ')

            # **Get all C files for the assignment (absolute paths)**
            code_files = (class_code / assignment).glob('**/*')

            # Track unique file extensions per student
            extensions = {}

            for code_file in code_files:
                if code_file.is_dir():
                    continue

                student_name = code_file.parent.name
                extension = code_file.suffix

                if student_name not in extensions:
                    extensions[student_name] = set()

                if extension not in extensions[student_name]:
                    extensions[student_name].add(extension)

                    # **Use absolute paths for student submission files**
                    abs_code_file = code_file.resolve()  # Get absolute path
                    f_out.write(f'"{abs_code_file}" ')

            # **Save results to a text file (absolute path)**
            moss_output_file = (moss_output_path / (assignment + '.txt')).resolve()
            f_out.write(f' | tee "{moss_output_file}" \n\n')

    # **Make the script executable**
    moss_command_path.chmod(moss_command_path.stat().st_mode | stat.S_IEXEC)

    print('=' * 40)
    print('MOSS CODE GENERATED')
    print('=' * 40)