import scipy
import matplotlib.pyplot as plt

#dy/dt = -0.5 * y
def modell(t, Ca2Plus, tauC,beta, v):
    if v > 30:
        d_Ca2Plus_dt = -(Ca2Plus/tauC) + beta
    else:
        d_Ca2Plus_dt = -(Ca2Plus/tauC)

    return [d_Ca2Plus_dt]

def ode_solution_points(function, state0, dt=0.01):
    pass



solution = scipy.integrate.solve_ivp(modell, t_span, y0)

plt.plot(solution.t, solution.y[0])
plt.xlabel('Zeit')
plt.ylabel('y(t)')
plt.show()



















