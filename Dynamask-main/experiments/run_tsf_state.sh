# State.
cd "$(dirname "$0")/.."

# train tfs

# -- cv=0
# python -m fit.evaluation.baselines --explainer tfs --cv 0 

# -- cv=1
python -m fit.evaluation.baselines --explainer tfs --cv 1 

# -- cv=2
python -m fit.evaluation.baselines --explainer tfs --cv 2 

# -- cv=3
python -m fit.evaluation.baselines --explainer tfs --cv 3

# -- cv=4
python -m fit.evaluation.baselines --explainer tfs --cv 4

# 2. Get Results
python -m experiments.results.state.get_results --CV 5 --explainers tfs
