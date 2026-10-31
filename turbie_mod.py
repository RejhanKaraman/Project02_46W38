
import numpy as np
from scipy.interpolate import interp1d


def load_wind(filename):
    """
    Load time and wind speed from a text file.
    """
    data = np.loadtxt(filename, comments="T")

    time = data[:, 0]
    wind_speed = data[:, 1]

    return time, wind_speed

def load_ct(filename, wind_speed):
    """
    Interpolate thrust coefficient for a given wind speed.
    """
    data = np.loadtxt(filename)

    v = data[:, 0]
    ct = data[:, 1]

    f_linear = interp1d(v, ct, kind='linear')

    ct_value = f_linear(wind_speed)

    return ct_value

def load_parameters(filename):
    """
    Load turbine parameters from a text file.
    """
    parameters = np.loadtxt(filename)

    return parameters



def build_matrices(parameters):
    """
    Build mass, damping and stiffness matrices.
    """
    mb = parameters[0]
    mn = parameters[1]
    mh = parameters[2]
    mt = parameters[3]

    c1 = parameters[4]
    c2 = parameters[5]

    k1 = parameters[6]
    k2 = parameters[7]

    m1 = 3 * mb
    m2 = mn + mh + mt

    M = np.array([
        [m1, 0],
        [0, m2]
    ])

    C = np.array([
        [c1, -c1],
        [-c1, c1 + c2]
    ])

    K = np.array([
        [k1, -k1],
        [-k1, k1 + k2]
    ])

    return M, C, K

def turbie_derivative(t, y, time, wind_speed, parameters, ct_value, A):
    """
    Calculate the derivatives of the Turbie 2DOF system.

    The state vector contains blade and tower displacements
    and velocities: [x1, x2, v1, v2].

    Returns the velocities and accelerations for numerical integration.
    """
    u = np.interp(t, time, wind_speed)
    x1, x2, v1, v2 = y

    m1 = 3 * parameters[0]
    m2 = parameters[1] + parameters[2] + parameters[3]

    c1 = parameters[4]
    c2 = parameters[5]

    k1 = parameters[6]
    k2 = parameters[7]

    rho = parameters[13]

    F_aero = 0.5 * rho * ct_value * A * (u - v1) * abs(u - v1)

    a1 = (F_aero - c1 * (v1 - v2) - k1 * (x1 - x2)) / m1

    a2 = (c1 * (v1 - v2) + k1 * (x1 - x2) - c2 * v2 - k2 * x2) / m2

    return [v1, v2, a1, a2]
