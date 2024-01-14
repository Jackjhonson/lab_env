# python -u -m evaluation.baselines --data simulation_spike --explainer fit --cv 0
python -u -m evaluation.baselines --data simulation_spike --explainer fit --cv 1 --train
python -u -m evaluation.baselines --data simulation_spike --explainer fit --cv 2 --train
python -u -m evaluation.baselines --data simulation_spike --explainer fit --cv 3 --train
python -u -m evaluation.baselines --data simulation_spike --explainer fit --cv 4 --train