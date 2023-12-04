import math


def compute_mu(wob, torque, bit_diameter):
    """Compute Mu
    input:
        wob: weight on bit (klbs)
        torque: torque (klbf-ft)
        bit_diameter: bit diameter (in)
    output:
        mu: mu
    """
    mu = torque / (wob * bit_diameter/36)
    # # Debug print
    # print(
    #     f"TORQUE: {torque}, WOB: {wob}, Mu: {mu}")
    return mu


# Function to compute MSE
def compute_mse(wob, bit_rpm, torque, rop, bit_diameter):
    """Compute Mechanical Specific Energy (ksi)
    input:
        wob: weight on bit (klbs)
        bit_rpm: rotary speed (rpm)
        torque: torque (klbf-ft)
        rop: rate of penetration (ft/hr)
        bit_diameter: bit diameter (in)
    output:
        mse: mechanical specific energy (ksi)
    """
    wob_term = wob / (bit_diameter/2)**2 * math.pi
    torque_term = 480 * torque * bit_rpm / (bit_diameter**2 * rop * 3.2808)

    return wob_term + torque_term
