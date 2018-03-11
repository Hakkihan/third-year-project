import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import math



lam = 10
v = 2
m = math.sqrt(lam) * v


def kink1(x):
	beta = -0.5
	gamma = 1 / math.sqrt(1 - beta**2)
	return v * math.tanh(m/math.sqrt(2) * gamma * x)
def kink1dot(x):
	beta = -0.5
	gamma = 1 / math.sqrt(1 - beta**2)
	return v * (1 - math.tanh(m/math.sqrt(2) * gamma * x)**2) * m * gamma * beta / math.sqrt(2)
	
def kink2(x):
	beta = 0.5
	gamma = 1 / math.sqrt(1 - beta**2)
	x0 = 12
	return v * math.tanh(-m/math.sqrt(2) * (gamma * x - x0))
def kink2dot(x):
	beta = 0.5
	gamma = 1 / math.sqrt(1 - beta**2)
	x0 = 12
	return -1 * v * (1 - math.tanh(-m/math.sqrt(2) * (gamma * x - x0))**2) * m * gamma * beta / math.sqrt(2)
	
	

def doubleKinkInitial(x):
		return kink1(x) + kink2(x)
def doubleKinkInitialDot(x):
		return kink1dot(x) + kink2dot(x)

def doubleWellPotential(phi):
	return phi * lam * (phi**2 - v**2)
def boundary(phi, pi):
	phi[0] = -2
	phi[-1] = 2
	

#1 = compare single point to exact result
#2 = compare global error with exact
#3 = compare 3 different resolutions
errorMode = 2
#used for number 1 and 3
pointToCompareTo = 1
#used for 1 and 2
def exactResult(x,t):
	beta = -0.5
	gamma = 1 / math.sqrt(1 - beta**2)
	return v * math.tanh(m/math.sqrt(2) * gamma * (x - beta * t))
	
x0 = -5
x1 = 10
finishTime = 10
potential = doubleWellPotential
initial = kink1
phiDotInitial = kink1dot

	
	
	
class List:
	def __init__(self, l):
		self.li = l
	def __iadd__(self, other):
		self.li = [x+y for x,y in zip(self.li, other.li)]
		return self
	def __add__(self, other):
		return List([x+y for x,y in zip(self.li, other.li)])
	def __mul__(self, other):
		return List([x * other for x in self.li])
	def __getitem__(self, key):
		return self.li[key]
	def __setitem__(self, key, value):
		self.li[key] = value
	def length(self):
		return len(self.li)

def calculateTotalError(phi, exact, xs, t):
	dx = xs[1] - xs[0]
	ErrorAtPoints = [(phi[n] - exact(xs[n], t))**2 for n in range(len(xs))]
	return math.sqrt(0.5 * dx * (2 * sum(ErrorAtPoints) - ErrorAtPoints[0] - ErrorAtPoints[-1]))

def getSecondDerivative(f,h):
	d2 = []
	
	#left side
	top = f[2] - 2*f[1] + f[0]
	d2.append(top / (h * h))
	
	#middle
	N = f.length()
	for n in range(1,N-1):
		top = f[n+1] - 2*f[n] + f[n-1]
		d2.append(top / (h * h))
		
	#right side
	top = f[-1] - 2*f[-2] + f[-3]
	d2.append(top / (h * h))
	
	return d2
	
	
def f(phi, pi, dx):
	d2 = getSecondDerivative(phi, dx)
	dVdp = [potential(p) for p in phi]
	return List([(d-v) for d,v in zip(d2, dVdp)])
		
def g(phi, pi, dx):
	return pi
		
		
def euler(phi, pi, dt, dx):
	pi += f(phi, pi, dx) * dt
	phi += g(phi, pi, dx) * dt

def rk2(phi, pi, dt, dx):
	k1 = f(phi, pi, dx) * dt
	l1 = g(phi, pi, dx) * dt
	
	k2 = f(phi + l1 * 0.5, pi + k1 * 0.5, dx) * dt
	l2 = g(phi + l1 * 0.5, pi + k1 * 0.5, dx) * dt
	
	pi += k2
	phi += l2
	
def rk4(phi, pi, dt, dx):
	k1 = f(phi, pi, dx) * dt
	l1 = g(phi, pi, dx) * dt
	
	k2 = f(phi + l1 * 0.5, pi + k1 * 0.5, dx) * dt
	l2 = g(phi + l1 * 0.5, pi + k1 * 0.5, dx) * dt
	
	k3 = f(phi + l2 * 0.5, pi + k2 * 0.5, dx) * dt
	l3 = g(phi + l2 * 0.5, pi + k2 * 0.5, dx) * dt
	
	k4 = f(phi + l3, pi + k3, dx) * dt
	l4 = g(phi + l3, pi + k3, dx) * dt
	
	pi += (k1 + k2 * 2 + k3 * 2 + k4) * (float(1)/6)
	phi += (l1 + l2 * 2 + l3 * 2 + l4) * (float(1)/6)
	
	

def run(dx, dt, timeStepMethod, outputFile = "output.mp4"):
	xs = np.arange(x0,x1,dx)
	phi = List([initial(x) for x in xs])
	pi = List([phiDotInitial(x) for x in xs])
	
	Error = [np.arange(0,finishTime,dt),[]]
	ErrorPoint = 0
	for i in range(len(xs)):
		if xs[i] >= pointToCompareTo:
			ErrorPoint = i
			break
	
	fig, ax = plt.subplots(figsize=(5, 4))
	ax.set(xlim=(x0, x1), ylim=(-5, 5))
	line = ax.plot(xs, pi.li, color='k', lw=2)[0]

	N = len(xs)

	def animate(i):
		timeStepMethod(phi, pi, dt, dx)
		
		#apply boundary conditions
		boundary(phi, pi)
		
		#add error to Error
		if errorMode == 1:
			Error[1].append(abs(phi[ErrorPoint] - exactResult(xs[ErrorPoint], dt * i)))
		elif errorMode == 2:
			Error[1].append(calculateTotalError(phi, exactResult, xs, dt * i))
		elif errorMode == 3:
			Error[1].append(phi)
			
		line.set_ydata(phi.li)
	
		
	anim = FuncAnimation(fig, animate, interval= dt*1000, frames=int(finishTime/dt))
	anim.save(outputFile)
	
	return Error

error1 = run(float(1)/50, float(1)/60, rk4, "output125.mp4")
error2 = run(float(1)/200, float(1)/250, rk4, "output250.mp4")

errorDivision = [error1[1][n] / error2[1][4*n] for n in range(len(error1[1]))]
orderOfConvergence = [math.log(error,2) if error != 0 else 0 for error in errorDivision]

plt.clf()
plt.plot(error1[0],error1[1][0:-1],'g')
plt.plot(error2[0],error2[1][0:-1],'b--')
plt.xlabel("t")
plt.ylabel("error")
plt.grid(True)
plt.savefig("errors.png")

plt.clf()
plt.plot(error1[0],orderOfConvergence[0:-1],'g')
plt.xlabel("t")
plt.ylabel("errorOrder")
plt.grid(True)
plt.savefig("errorOrder.png")
