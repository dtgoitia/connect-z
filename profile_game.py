from cProfile import Profile
import connectz
import pathlib
import subprocess
import sys

def main():
    profiler = Profile()
    profiler.enable()
    connectz.main()
    profiler.disable()

    # Dump stats
    file_name = sys.argv[1]
    file_path = pathlib.Path.cwd() / 'profilling' / file_name
    profiler.dump_stats(f'{file_path}.pstats')

    # Create chart from stats
    ps = subprocess.Popen(['gprof2dot', '-f', 'pstats', f'{file_path}.pstats'], stdout=subprocess.PIPE)
    output = subprocess.check_output(['dot', '-Tpng', '-o', f'{file_path}.png'], stdin=ps.stdout)
    ps.wait()


if __name__ == '__main__':
    main()
