import numpy as np
import matplotlib.pyplot as plt

from scipy.integrate import solve_ivp

from turbie_mod import load_wind, load_ct, load_parameters, build_matrices, turbie_derivative


# Input files
ct_filename = "inputs/CT.txt"
parameters_filename = "inputs/turbie_parameters.txt"

# Turbine parameters
parameters = load_parameters(parameters_filename)

M, C, K = build_matrices(parameters)

Dr = parameters[12]
A = np.pi * Dr**2 / 4

# Initial conditions: x1, x2, v1, v2
y0 = [0.0, 0.0, 0.0, 0.0]


# Wind turbulence categories
TI_values = ["0.05", "0.1", "0.15"]

# Simulate all wind speeds and turbulence categories
for TI in TI_values:

    # Store statistics for this turbulence category
    statistics = []

    for U in range(4, 26):

        filename = (
            "inputs/wind_files/wind_TI_" + TI
            + "/wind_" + str(U) + "_ms_TI_" + TI + ".txt"
        )

        time, wind_speed = load_wind(filename)

        print("Mean wind speed:", np.mean(wind_speed))
        print("Minimum wind speed for Ct table:", 4.0)

        # Thrust coefficient from mean wind speed
        ct_value = load_ct(ct_filename, np.round(np.mean(wind_speed), 4))

        # Numerical integration
        solution = solve_ivp(
            turbie_derivative,
            [time[0], time[-1]],
            y0,
            t_eval=time,
            args=(time, wind_speed, parameters, ct_value, A)
        )

        print("Wind speed:", U, "m/s, TI:", TI)
        print("Simulation completed:", solution.success)

        if not solution.success:
            raise RuntimeError(solution.message)

        # Save simulation results
        results = np.column_stack((
            solution.t,
            solution.y[0],
            solution.y[1]
        ))

        output_filename = (
            "outputs/wind_TI_" + TI
            + "/turbie_" + str(U) + "_ms_TI_" + TI + ".txt"
        )

        np.savetxt(
           output_filename,
           results,
           fmt=["%.2f", "%.8f", "%.8f"],
           header="Time[s] Blade_displacement[m] Tower_displacement[m]"
        )
 

        print("Saved:", output_filename)

        # Mean and standard deviation of displacements
        blade_mean = np.mean(solution.y[0])
        blade_std = np.std(solution.y[0])

        tower_mean = np.mean(solution.y[1])
        tower_std = np.std(solution.y[1])

        # Store statistics for this wind speed
        statistics.append([
            U,
            blade_mean,
            blade_std,
            tower_mean,
            tower_std
        ])

    # Save statistics for this turbulence category
    statistics = np.array(statistics)

    statistics_filename = (
        "outputs/wind_TI_" + TI
        + "/statistics_TI_" + TI + ".txt"
    )

    np.savetxt(
        statistics_filename,
        statistics,
        fmt=["%.0f", "%.6f", "%.6f", "%.6f", "%.6f"],
        header="Wind_speed[m/s] Blade_mean[m] Blade_std[m] Tower_mean[m] Tower_std[m]"
    )

    print("Statistics saved:", statistics_filename)


# --------------------------------------------------
# 1. Mean blade displacement vs wind speed
# --------------------------------------------------

plt.figure()

for TI in TI_values:

    filename = (
        "outputs/wind_TI_" + TI
        + "/statistics_TI_" + TI + ".txt"
    )

    data = np.loadtxt(filename)

    plt.plot(data[:, 0], data[:, 1], label="TI = " + TI)

plt.xlabel("Mean wind speed [m/s]")
plt.ylabel("Mean blade displacement [m]")
plt.title("Mean blade displacement vs wind speed")
plt.legend()
plt.grid()
plt.tight_layout()

plt.savefig("outputs/mean_blade_displacement.png", dpi=300)


# --------------------------------------------------
# 2. Standard deviation of blade displacement
# --------------------------------------------------

plt.figure()

for TI in TI_values:

    filename = (
        "outputs/wind_TI_" + TI
        + "/statistics_TI_" + TI + ".txt"
    )

    data = np.loadtxt(filename)

    plt.plot(data[:, 0], data[:, 2], label="TI = " + TI)

plt.xlabel("Mean wind speed [m/s]")
plt.ylabel("Standard deviation of blade displacement [m]")
plt.title("Blade displacement standard deviation vs wind speed")
plt.legend()
plt.grid()
plt.tight_layout()

plt.savefig("outputs/std_blade_displacement.png", dpi=300)


# --------------------------------------------------
# 3. Mean tower displacement vs wind speed
# --------------------------------------------------

plt.figure()

for TI in TI_values:

    filename = (
        "outputs/wind_TI_" + TI
        + "/statistics_TI_" + TI + ".txt"
    )

    data = np.loadtxt(filename)

    plt.plot(data[:, 0], data[:, 3], label="TI = " + TI)

plt.xlabel("Mean wind speed [m/s]")
plt.ylabel("Mean tower displacement [m]")
plt.title("Mean tower displacement vs wind speed")
plt.legend()
plt.grid()
plt.tight_layout()

plt.savefig("outputs/mean_tower_displacement.png", dpi=300)


# --------------------------------------------------
# 4. Standard deviation of tower displacement
# --------------------------------------------------

plt.figure()

for TI in TI_values:

    filename = (
        "outputs/wind_TI_" + TI
        + "/statistics_TI_" + TI + ".txt"
    )

    data = np.loadtxt(filename)

    plt.plot(data[:, 0], data[:, 4], label="TI = " + TI)

plt.xlabel("Mean wind speed [m/s]")
plt.ylabel("Standard deviation of tower displacement [m]")
plt.title("Tower displacement standard deviation vs wind speed")
plt.legend()
plt.grid()
plt.tight_layout()

plt.savefig("outputs/std_tower_displacement.png", dpi=300)


# --------------------------------------------------
# 5. Time histories for one selected wind case
# --------------------------------------------------

# Selected case: 10 m/s, TI = 0.1
U = 10
TI = "0.1"

# Load wind speed time history
wind_filename = (
    "inputs/wind_files/wind_TI_" + TI
    + "/wind_" + str(U) + "_ms_TI_" + TI + ".txt"
)

wind_data = np.loadtxt(wind_filename, skiprows=1)

wind_time = wind_data[:, 0]
wind_speed = wind_data[:, 1]


# Load simulated blade and tower displacements
results_filename = (
    "outputs/wind_TI_" + TI
    + "/turbie_" + str(U) + "_ms_TI_" + TI + ".txt"
)

results = np.loadtxt(results_filename)

time = results[:, 0]
blade_displacement = results[:, 1]
tower_displacement = results[:, 2]


# --------------------------------------------------
# 6. Wind speed time history
# --------------------------------------------------

plt.figure()

plt.plot(wind_time, wind_speed)

plt.xlabel("Time [s]")
plt.ylabel("Wind speed [m/s]")
plt.title("Wind speed time history - 10 m/s, TI = 0.1")
plt.grid()
plt.tight_layout()

plt.savefig("outputs/wind_speed_time_history.png", dpi=300)


# --------------------------------------------------
# 7. Blade displacement time history
# --------------------------------------------------

plt.figure()

plt.plot(time, blade_displacement)

plt.xlabel("Time [s]")
plt.ylabel("Blade displacement [m]")
plt.title("Blade displacement time history - 10 m/s, TI = 0.1")
plt.grid()
plt.tight_layout()

plt.savefig("outputs/blade_displacement_time_history.png", dpi=300)


# --------------------------------------------------
# 8. Tower displacement time history

plt.figure()

plt.plot(time, tower_displacement)

plt.xlabel("Time [s]")
plt.ylabel("Tower displacement [m]")
plt.title("Tower displacement time history - 10 m/s, TI = 0.1")
plt.grid()
plt.tight_layout()

plt.savefig("outputs/tower_displacement_time_history.png", dpi=300)


plt.show()
