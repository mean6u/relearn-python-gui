import scipy
import numpy as np
import matplotlib.pyplot as plt

#dy/dt = -0.5 * y
def modell(t, state0, tauCa=10000, beta=0.001,  
           a=0.1, b=0.2, c=-65, d=2, I=10, k1=0.04, k2=5, k3=140):

    Ca2Plus, u, v = state0

    dv_dt = k1*v**2 +k2*v + k3 - u + I

    du_dt = a*(b*v - u)

    if dv_dt >= 30:
        v = c
        u = u + d

    if v > 30:
        d_Ca2Plus_dt = -(Ca2Plus/tauCa) + beta
    else:
        d_Ca2Plus_dt = -(Ca2Plus/tauCa)

    return [d_Ca2Plus_dt, du_dt, dv_dt]

def ode_solution_points(function, state0, t, dt=0.01):
    solution = scipy.integrate.solve_ivp(
        function, 
        t_span=(0, t),
        y0=state0, 
        t_eval=np.arange(0, t, dt)
    ) 
    return solution






