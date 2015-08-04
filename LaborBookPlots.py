import numpy as np
import matplotlib.pyplot as plt
import os
import re

plt.clf()
maxes = []
ys = []
for root, curdir, f in os.walk("."):
	for name in f:
		if "scan_" in name and "0.006-0-50" in name and not ".csv" in name and not ".png" in name:
			#we have a numpy binary state, load it plot it, read one line and plot that too (take line 15) x from 17 - 28
			arr = np.load(os.path.join(root,name))
			#plt.imshow(arr, interpolation="None")
			#plt.savefig(name+".png")
			#plt.clf()
			data = arr[15,17:28]
			n = name
			r = re.compile("\d+mA")
			match = r.search(name)
			if match is not None:
				n = match.group(0)
			plt.plot(np.linspace(0,len(data)-1,len(data)),data, "-.", label=n) #subtract what should be noise
			maxes += [np.max(data)]
			ys += [np.argmax(data)]
			print(np.argmax(data), np.max(data), maxes)
plt.scatter(ys, maxes)
box = plt.gca().get_position()
plt.gca().set_position([box.x0, box.y0, box.width * 0.8, box.height])
plt.legend(loc = "center left", bbox_to_anchor=(1,0.5))
plt.savefig("intens_comb.png")
