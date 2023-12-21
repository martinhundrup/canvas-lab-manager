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
    f_out = open(moss_command_path.relative_to('.'), 'w')

    for assignment in assignments_list:
        # Write init code for moss commands
        f_out.write('cd {} \n'.format(class_code.relative_to('.')))
        # TODO: Hard coded path to mass, change later
        f_out.write('{} -d -l {} -m 1000000 '.format('../../../../moss', language))
        f_out.write('-c "{a} in {c}" '.format(a=assignment, c=course_dir.name))

        # Grab all allowed code files from the cleaned dir
        code_files = (class_code / assignment).glob('**/*')

        # Extract out the extensions
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
                code_dir_path = code_dir_path.replace("'", "\\'")
                code_dir_path = code_dir_path.replace("(", "\\(")
                code_dir_path = code_dir_path.replace(")", "\\)")
                f_out.write(code_dir_path + '/*' + extension + ' ')

        # Save results of moss runs to txt
        f_out.write(' | tee {} \n'.format(str((moss_output_path / (assignment + '.txt')).resolve()).replace(' ', '\\ ')))
        # TODO: Hard coded path to mass, change later
        f_out.write('cd {} \n'.format('../../../..'))
        f_out.write('\n')

    # Close out the file
    f_out.close()

    # Set file to be executable
    moss_command_path.chmod(moss_command_path.stat().st_mode | stat.S_IEXEC)

    print('=' * 40)
    print('MOSS CODE GENERATED')
    print('=' * 40)

    return
