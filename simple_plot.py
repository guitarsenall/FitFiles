import numpy as np

def moving_average(x, n=30) :
	nX = len(x)
	y = np.zeros(nX)
	for i in range(nX):
		if i >= n-1:
			y[i] = np.sum( x[i-n+1:i+1] ) / n
		elif i==0:
			y[i] = x[i]
		else:
			y[i] = np.sum( x[0:i+1] ) / (i+1)
	return y

n = 300	# interval length, sec
interval = np.concatenate(( \
					np.ones(n)*50, \
					np.ones(n)*300 ))
nInt = 5	# number of intervals
x = interval
for i in range(nInt):
	x = np.concatenate((x,interval))
nPts = len(x)

fp = moving_average(x, n=30)

from pylab import *
t = arange(0.0, nPts, 1.0)
plot(t, x)
plot(t, fp)
xlabel('time (s)')
ylabel('power (w)')
title('filtered intervals')
grid(True)
show()

# compute normalized power
NPwr = np.average(fp**4)**0.25
print('normalized power = %i watts' \
			% NPwr)

