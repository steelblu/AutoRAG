import os
from typing import List, Callable, Dict
import pandas as pd

from autorag.strategy import measure_speed


def run_parser(
	modules: List[Callable],
	module_params: List[Dict],
	data_path_glob: str,
	trial_path: str,
):
	results, execution_times = zip(
		*map(
			lambda x: measure_speed(x[0], data_path_glob=data_path_glob, **x[1]),
			zip(modules, module_params),
		)
	)
	average_times = list(map(lambda x: x / len(results[0]), execution_times))

	# save results to parquet files
	filepaths = list(
		map(lambda x: os.path.join(trial_path, f"{x}.parquet"), range(len(modules)))
	)
	list(map(lambda x: x[0].to_parquet(x[1], index=False), zip(results, filepaths)))
	filenames = list(map(lambda x: os.path.basename(x), filepaths))

	summary_df = pd.DataFrame(
		{
			"filename": filenames,
			"module_name": list(map(lambda module: module.__name__, modules)),
			"module_params": module_params,
			"execution_time": average_times,
		}
	)
	summary_df.to_csv(os.path.join(trial_path, "summary.csv"), index=False)
	return summary_df
