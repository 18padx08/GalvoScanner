import numpy as np

focus = 0
ran = np.linspace(0,5,100)
hook = open("tmpHook.hk", 'w')
count = 0
for ele in ran:
	f = open("zline.%d.cfg"%count,'w')
	f.write("""
		{
	"imports" : ["scanner_config.cfg"],
	"settings" : 
				{
					"focus" : %d,
					"xsteps" : [-0.00072],
					"ysteps" : [0.0033]
				}				
}
		"""%ele)
	f.close()
	hook.write("""
		loadConfig(oneline/zline.%d.cfg)
scanSample()
saveState(oneline/zline%d.npy)
		"""%(count,count))
	count += 1

hook.close()
