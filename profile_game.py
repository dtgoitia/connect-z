from cProfile import Profile
import connectz
import pathlib
import subprocess
import sys
import time

def main():
    print('Mocking command arguments...')
    file_name = sys.argv[1]
    file_path = pathlib.Path.cwd() / 'profilling' / file_name
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
    print(f'Execution time: {end - start:.4f}s')


if __name__ == '__main__':
    main()
