from cProfile import Profile
import connectz
import pathlib
import shutil
import statistics
import subprocess
import sys
import time

from create_game import create_game


PROFILLING_DIR = 'profilling'
FILE_NAME = 'game_for_profilling'


def profile_game(file_name: str):
    print('Mocking command arguments...')
    file_path = pathlib.Path.cwd() / PROFILLING_DIR / file_name
    if len(sys.argv) == 1:
        sys.argv.append(str(file_path))
    else:
        sys.argv[1] = str(file_path)

    profiler = Profile()
    print('Collecting stats...')
    profiler.enable()
    print('Run connectz.main()')
    start = time.time()
    connectz.main()
    end = time.time()
    profiler.disable()

    # Dump stats
    print('Dumping collected stats...', end='')
    profiler.dump_stats(f'{file_path}.pstats')
    print(' done')

    # Create chart from stats
    print('Creating profile tree...', end='')
    ps = subprocess.Popen(['gprof2dot', '-f', 'pstats', f'{file_path}.pstats'], stdout=subprocess.PIPE)
    output = subprocess.check_output(['dot', '-Tpng', '-o', f'{file_path}.png'], stdin=ps.stdout)
    ps.wait()
    print(' done')

    execution_time = end-start
    print(f'Execution time: {execution_time:.4f}s')
    return execution_time


def main():
    game_path = create_game(FILE_NAME)
    durations = []

    for n in range(4):
        file_name = f'{FILE_NAME}_{n}'
        game_copy_path = game_path.parent / file_name
        shutil.copyfile(game_path, game_copy_path)
        duration = profile_game(file_name)
        durations.append(duration)

    durations_file = pathlib.Path.cwd() / PROFILLING_DIR / 'durations'
    with durations_file.open('a') as f:
        mean = statistics.mean(durations)
        print(f'Average execution time: {mean:.4f}s')
        formatted = [f'{t:.4f}' for t in (mean, *durations)]
        line = f"{' '.join(formatted)}\n"
        f.write(line)


if __name__ == '__main__':
    main()
