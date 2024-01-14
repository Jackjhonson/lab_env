python -u -m evaluation.baselines --data simulation_spike --explainer tfs --cv 0
python -u -m evaluation.baselines --data simulation_spike --explainer tfs --cv 1 --train
python -u -m evaluation.baselines --data simulation_spike --explainer tfs --cv 2 --train
python -u -m evaluation.baselines --data simulation_spike --explainer tfs --cv 3 --train
python -u -m evaluation.baselines --data simulation_spike --explainer tfs --cv 4 --train