import numpy as np
import re


bg, max = [ [np.load(sortname)[15,17] for sortname in [sortedname for sortedname in sorted([name for root, top, f in os.walk(".") for name in f if "csv" not in name and "png" not in name and "scan" in name and "0.006" in name], key = lambda sn: int(re.search("\d+mA",sn).group(0).replace("mA", "")))]],[np.max(np.load(sortname)[15,17:28]) for sortname in [sortedname for sortedname in sorted([name for root, top, f in os.walk(".") for name in f if "csv" not in name and "png" not in name and "scan" in name and "0.006" in name], key = lambda sn: int(re.search("\d+mA",sn).group(0).replace("mA", "")))]]]
