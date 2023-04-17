# State.
cd "$(dirname "$0")/.."



# 2. Get Results
python -m experiments.results.state.get_results --CV 5 --explainers dynamask fo afo deep_lift fit retain
