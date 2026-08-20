import multiprocessing
import subprocess


def run_job(n):
    with open(f"output_{n}.txt", "w") as out_file:
        subprocess.run(["./hello", str(n)], stdout=out_file)


if __name__ == "__main__":
    with multiprocessing.Pool(processes=10) as pool:
        pool.map(run_job, range(1, 11))
