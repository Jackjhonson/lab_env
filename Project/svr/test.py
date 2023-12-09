import imp
from math import nan
import torch

i = [1,2,3,nan]
t = torch.tensor(i)
print(t)