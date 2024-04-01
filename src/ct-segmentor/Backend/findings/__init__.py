
import yaml
from pathlib import Path
from .gen_findings import radmix

with open(Path(__file__).parent / "backend_radmix.yaml", 'r') as f:
    valuesYaml = yaml.load(f, Loader=yaml.FullLoader)

model = radmix(valuesYaml)
