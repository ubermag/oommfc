import contextlib
import datetime
import glob
import threading
import time

from tqdm.auto import tqdm


class ProgressBar(threading.Thread):
    """Tqdm progress bar thread for OOMMF progress.

    Parameters
    ----------
    total : int

        Total number of output files written to disk.

    runner_name : str

        Name of the OOMMF runner.

    glob_name : str

        Name of the output files used for globbing in the output directory.
    """

    INTERVAL = 1

    def __init__(self, total, runner_name, glob_name):
        super().__init__()
        self.bar = tqdm(
            total=total,
            desc=f"Running OOMMF ({runner_name})",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} files written [{elapsed}]",
        )
        self._terminate = False
        self.glob_name = glob_name

    def run(self):
        """Update the progress bar once per second and close when terminating."""
        while not self._terminate:
            self.bar.n = len(glob.glob(f"{self.glob_name}*.omf"))
            self.bar.refresh()
            time.sleep(self.INTERVAL)
        self.bar.n = len(glob.glob(f"{self.glob_name}*.omf"))
        self.bar.refresh()
        self.bar.close()

    def terminate(self):
        """Stop a running progress bar thread after the current iteration."""
        self._terminate = True
        self.join()


@contextlib.contextmanager
def bar(total, runner_name, glob_name):
    progress_bar_thread = ProgressBar(total, runner_name, glob_name)
    progress_bar_thread.start()
    try:
        yield
    finally:
        progress_bar_thread.terminate()


@contextlib.contextmanager
def summary(runner_name):
    now = datetime.datetime.now()
    timestamp = "{}/{:02d}/{:02d} {:02d}:{:02d}".format(
        now.year, now.month, now.day, now.hour, now.minute
    )
    print(
        f"Running OOMMF ({runner_name})[{timestamp}]... ",
        end="",
    )
    tic = time.time()
    try:
        yield
    finally:
        toc = time.time()
        seconds = "({:0.1f} s)".format(toc - tic)
        print(seconds)  # append seconds to the previous print.