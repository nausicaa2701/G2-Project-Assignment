"""CLI: run the storyline experiments and write results/story/ for the app.

Examples
  python run_story.py --part 2                      # E2.1-E2.3, seeds 0-4, 5 folds
  python run_story.py --part 2 --seeds 0 1 --folds 3
Parts 1 and 3 plug in the same way: add wdi/story/part{N}.py with a run(seeds, folds, out, log) function.
"""
import argparse
import importlib
import time

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument("--part", type=int, nargs="+", default=[2], choices=[1, 2, 3])
p.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
p.add_argument("--folds", type=int, default=5)
p.add_argument("--out", default="results/story")
a = p.parse_args()

t0 = time.time()
for part in a.part:
    try:
        mod = importlib.import_module(f"wdi.story.part{part}")
    except ModuleNotFoundError:
        print(f"part {part}: wdi/story/part{part}.py not written yet, skipped")
        continue
    mod.run(seeds=a.seeds, folds=a.folds, out=a.out, log=lambda m: print(f"[{time.time() - t0:5.0f}s] {m}", flush=True))
print(f"done in {time.time() - t0:.0f}s -> {a.out}/")
