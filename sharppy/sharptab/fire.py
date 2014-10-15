from sharppy.sharptab import *
import numpy as np

def fosberg(prof):
    tmpf = thermo.ctof(prof.tmpc[prof.get_sfc()])
    fmph = utils.KTS2MPH(prof.wspd[prof.get_sfc()])

    rh = 0 # Not sure where rh comes from yet, maybe BL RH?

    if (rh <= 10):
        em = 0.03229 + 0.281073*rh - 0.000578*rh*tmpf
    elif (10 > rh <= 50):
        em = 2.22749 + 0.160107*rh - 0.014784*tmpf
    else:
        em = 21.0606 + 0.005565*rh*rh - 0.00035*rh*tmpf - 0.483199*rh

    em30 = em/30.
    u_sq = fmph * fmph
    fmdc = 1 - 2*em30 + 1.5*em30*em30 - 0.5*em30*em30*em30

    param = (fmdc*np.sqrt(1+u_sq))/0.3002

    return param
