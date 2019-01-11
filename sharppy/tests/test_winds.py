import numpy as np
import numpy.ma as ma
import numpy.testing as npt
import sharppy.sharptab.winds as winds
import sharppy.sharptab.utils as utils
import sharppy.sharptab.interp as interp
from sharppy.sharptab.profile import Profile
import test_profile


prof = test_profile.TestProfile().prof


import time
def test_mean_wind():
    returned = winds.mean_wind(prof)
    correct_u, correct_v = 27.347100616691097, 1.7088123127933754
    npt.assert_almost_equal(returned, [correct_u, correct_v])


def test_mean_wind_npw():
    returned = winds.mean_wind_npw(prof)
    correct_u, correct_v = 31.831128476043443, -0.40994804851302158
    npt.assert_almost_equal(returned, [correct_u, correct_v])


def test_sr_wind():
    input_stu = 10
    input_stv = 10
    returned = winds.sr_wind(prof, stu=input_stu, stv=input_stv)
    correct_u, correct_v = 17.347100616691126, -8.2911876872066141
    npt.assert_almost_equal(returned, [correct_u, correct_v])


def test_sr_wind_npw():
    input_stu = 10
    input_stv = 10
    returned = winds.sr_wind_npw(prof, stu=input_stu, stv=input_stv)
    correct_u, correct_v = 21.831128476043443, -10.40994804851302158
    npt.assert_almost_equal(returned, [correct_u, correct_v])


def test_wind_shear():
    agl1 = 0
    agl2 = 1000
    msl1 = interp.to_msl(prof, agl1)
    msl2 = interp.to_msl(prof, agl2)
    pbot = interp.pres(prof, msl1)
    ptop = interp.pres(prof, msl2)
    correct_u, correct_v = -2.625075135691132, 10.226725739920353
    returned = winds.wind_shear(prof, pbot, ptop)
    npt.assert_almost_equal(returned, [correct_u, correct_v])


def test_non_parcel_bunkers_motion():
    correct = [10.532915762684453, -7.863859696750608,
               20.924864405622614, 19.379065415942257]
    returned = winds.non_parcel_bunkers_motion(prof)
    npt.assert_almost_equal(returned, correct)


def test_helicity():
    agl1 = 0.
    agl2 = 3000.
    input_ru = 10.5329157627
    input_rv = -7.86385969675
    correct = [284.9218078420389, 302.9305759626597, -18.008768120620786]
    returned = winds.helicity(prof, agl1, agl2, stu=input_ru,
                              stv=input_rv, exact=True)
    npt.assert_almost_equal(returned, correct)

    correct = [285.00199936592099, 302.99422077416955, -17.992221408248568]
    returned = winds.helicity(prof, agl1, agl2, stu=input_ru,
                              stv=input_rv, exact=False)
    npt.assert_almost_equal(returned, correct)

"""
def test_max_wind():
    agl1 = 0.
    agl2 = 30000
    correct = [73.860581475915609, -13.023613325019747, 179.]
    returned = winds.max_wind(prof, agl1, agl2)
    npt.assert_almost_equal(returned, correct)

    correct_u = [73.86058147591561, 73.86058147591561]
    correct_v = [-13.023613325019747, -13.023613325019747]
    correct_p = [175.0, 172.64]
    correct = [correct_u, correct_v, correct_p]
    returned = winds.max_wind(prof, agl1, agl2, all=True)
    npt.assert_almost_equal(returned, correct)
"""

def test_corfidi_mcs_motion():
    correct = [34.597990416506541, -17.61022875300797,
               64.319470111830171, -16.945587838431905]
    returned = winds.corfidi_mcs_motion(prof)
    npt.assert_almost_equal(returned, correct)


def test_mbe_vectors():
    correct = [34.597990416506541, -17.61022875300797,
               64.319470111830171, -16.945587838431905]
    returned = winds.mbe_vectors(prof)
    npt.assert_almost_equal(returned, correct)

def test_critical_angle():
    correct = [169.2658597]
    returned = [winds.critical_angle(prof)]
    npt.assert_almost_equal(returned, correct)

