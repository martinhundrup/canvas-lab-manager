import pathlib
import pandas as pd
import stat
import subprocess


def run_moss(course_dir: pathlib.Path, assignments_list: list, language: str = 'cc') -> None:
    generate_moss(course_dir, assignments_list, language)
    subprocess.call(['sh', str((course_dir / 'run_moss.sh').relative_to('.'))])
    return


def generate_moss(course_dir: pathlib.Path, assignments_list: list, language: str = 'cc') -> None:
    # Construct moss command here
    moss_command_path = course_dir / 'run_moss.sh'
    moss_output_path = course_dir / 'moss_output'
    moss_output_path.mkdir(exist_ok=True, parents=True)

    # Code dir
    class_code = course_dir / 'assignments'

    # Open file (w to always clean it out beforehand)
    with open(moss_command_path.relative_to('.'), 'w') as f_out:
        for assignment in assignments_list:
            # Write init code for moss commands
            f_out.write(f'cd {class_code.relative_to(".")} \n')
            f_out.write(f'../../../moss -d -l {language} -m 1000000 ')
            f_out.write(f'-c "{assignment} in {course_dir.name}" ')

            # Grab all allowed code files from the cleaned dir
            code_files = (class_code / assignment).glob('**/*')

            # Extract extensions and prepare file paths
            extensions = dict()
            for code_file in code_files:
                if code_file.is_dir():
                    continue

                student_name = code_file.parent.name

                if student_name not in extensions:
                    extensions[student_name] = set()

                extension = code_file.suffix

                if extension not in extensions[student_name]:
                    extensions[student_name].add(extension)
                    code_dir_path = str(code_file.relative_to(class_code).parent)
                    code_dir_path = code_dir_path.replace(' ', '\\ ')
                    f_out.write(code_dir_path + '/*' + extension + ' ')

            # Save results of moss runs to txt
            moss_output_file = moss_output_path / (assignment + '.txt')
            f_out.write(f' | tee {str(moss_output_file.resolve()).replace(" ", "\\ ")} \n')
            f_out.write('cd ../../.. \n')
            f_out.write('\n')

    # Set file to be executable
    moss_command_path.chmod(moss_command_path.stat().st_mode | stat.S_IEXEC)

    print('=' * 40)
    print('MOSS CODE GENERATED')
    print('=' * 40)


    return
