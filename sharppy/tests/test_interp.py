import numpy as np
import numpy.ma as ma
import numpy.testing as npt
import sharppy.sharptab.interp as interp
from sharppy.sharptab.utils import vec2comp
from sharppy.sharptab.profile import Profile
import test_profile as tp


prof = tp.TestProfile().prof


def test_pres():
    input_z = 1000.
    correct_p = 903.8343884049208
    returned_p = interp.pres(prof, input_z)
    npt.assert_almost_equal(returned_p, correct_p)

    input_z = [1000., 3000., 6000.]
    correct_p = np.asarray([903.834388405, 710.02200544, 482.16636819])
    returned_p = interp.pres(prof, input_z)
    npt.assert_almost_equal(returned_p, correct_p)


def test_hght():
    input_p = 900
    correct_z = 1036.0022240687013
    returned_z = interp.hght(prof, input_p)
    npt.assert_almost_equal(returned_z, correct_z)

    input_p = [900, 800, 600, 400]
    correct_z = np.asarray([1036.0022240687013, 2020.3374024,
                            4330.6739399, 7360.])
    returned_z = interp.hght(prof, input_p)
    npt.assert_almost_equal(returned_z, correct_z)


def test_temp():
    input_p = 900
    correct_t = 14.589978853117268
    returned_t = interp.temp(prof, input_p)
    npt.assert_almost_equal(returned_t, correct_t)

    input_p = [900, 800, 600, 400]
    correct_t = np.asarray([14.589978853117268, 8.3624187,
                            -7.48619696, -29.7])
    returned_t = interp.temp(prof, input_p)
    npt.assert_almost_equal(returned_t, correct_t)


def test_dwpt():
    input_p = 900
    correct_t = 11.52599445805832
    returned_t = interp.dwpt(prof, input_p)
    npt.assert_almost_equal(returned_t, correct_t)

    input_p = [900, 800, 600, 400]
    correct_t = np.asarray([11.52599445805832, 6.07174951,
                            -13.34348479, -35.7])
    returned_t = interp.dwpt(prof, input_p)
    npt.assert_almost_equal(returned_t, correct_t)


def test_vtmp():
    input_p = 900
    correct_v = 16.24810167687504
    returned_v = interp.vtmp(prof, input_p)
    npt.assert_almost_equal(returned_v, correct_v, decimal=2)

    input_p = [900, 800, 600, 400]
    correct_v = np.asarray([16.24810167687504, 9.62205272,
                            -7.11816357, -29.63245875])
    returned_v = interp.vtmp(prof, input_p)
    npt.assert_almost_equal(returned_v, correct_v, decimal=2)


def test_components():
    input_p = 900
    correct_u, correct_v = -5.53976475, 20.6746835
    correct = [correct_u, correct_v]
    returned = interp.components(prof, input_p)
    npt.assert_almost_equal(returned, correct)

    input_p = [900, 800, 600, 400]
    correct_u = np.asarray([-5.53976475, 5.95267234,
                            23.10783339, 42.])
    correct_v = np.asarray([20.6746835, 15.54170573,
                            -9.37502817, 0])
    correct = [correct_u, correct_v]
    returned = interp.components(prof, input_p)
    npt.assert_almost_equal(returned, correct)


def test_vec():
    input_p = 900
    correct_wdir, correct_wspd = 165., 21.40400736
    correct = [correct_wdir, correct_wspd]
    returned = interp.vec(prof, input_p)
    npt.assert_almost_equal(returned, correct)

    input_p = [900, 800, 600, 400]
    correct_wdir = np.asarray([165., 200.95747979,
                               292.08277812, 270.])
    correct_wspd = np.asarray([21.40400736, 16.64268383,
                               24.93718343, 42.])
    correct = [correct_wdir, correct_wspd]
    returned = interp.vec(prof, input_p)
    npt.assert_almost_equal(returned, correct)


def test_to_agl():
    input_z = 1000.
    correct_agl = 643.0
    returned_agl = interp.to_agl(prof, input_z)
    npt.assert_almost_equal(returned_agl, correct_agl)

    input_z = [1000., 3000., 6000.]
    correct_agl = [643., 2643., 5643.]
    returned_agl = interp.to_agl(prof, input_z)
    npt.assert_almost_equal(returned_agl, correct_agl)


def test_to_msl():
    input_z = 1000.
    correct_agl = 1357.
    returned_agl = interp.to_msl(prof, input_z)
    npt.assert_almost_equal(returned_agl, correct_agl)

    input_z = [1000., 3000., 6000.]
    correct_agl = [1357., 3357., 6357]
    returned_agl = interp.to_msl(prof, input_z)
    npt.assert_almost_equal(returned_agl, correct_agl)



