''' Frequently used functions '''
import numpy as np
import numpy.ma as ma
import numpy.testing as npt
from sharppy.sharptab.constants import MISSING, TOL
from sharppy.sharptab import utils as utils


# vec2comp Tests
def test_vec2comp_single():
    input_wdir = 225
    input_wspd = 7.0710678118654755
    correct_u = 5
    correct_v = 5
    returned_u, returned_v = utils.vec2comp(input_wdir, input_wspd)
    npt.assert_almost_equal(returned_u, correct_u)
    npt.assert_almost_equal(returned_v, correct_v)

def test_vec2comp_array_like():
    input_wdir = [0, 45, 90, 135, 180, 225, 270, 315, 360]
    input_wspd = [5, 10, 15, 20, 25, 30, 35, 40, 45]
    correct_u = [0, -7.0710678118654746, -15, -14.142135623730951, 0,
        21.213203435596423, 35, 28.284271247461909, 0]
    correct_v = [-5, -7.0710678118654746, 0, 14.142135623730951, 25,
        21.213203435596423, 0, -28.284271247461909, -45]
    correct_u = np.asanyarray(correct_u).astype(np.float64)
    correct_v = np.asanyarray(correct_v).astype(np.float64)
    returned_u, returned_v = utils.vec2comp(input_wdir, input_wspd)
    npt.assert_almost_equal(returned_u, correct_u)
    npt.assert_almost_equal(returned_v, correct_v)

def test_vec2comp_zeros():
    input_wdir = [0, 90, 180, 270, 360]
    input_wspd = [10, 20, 30, 40, 50]
    correct_u = [0, -20, 0, 40, 0]
    correct_v = [-10, 0, 30, 0, -50]
    correct_u = np.asanyarray(correct_u).astype(np.float64)
    correct_v = np.asanyarray(correct_v).astype(np.float64)
    returned_u, returned_v = utils.vec2comp(input_wdir, input_wspd)
    npt.assert_equal(returned_u, correct_u)
    npt.assert_equal(returned_v, correct_v)

def test_vec2comp_default_missing_val_single():
    input_wdir = MISSING
    input_wspd = 30
    returned_u, returned_v = utils.vec2comp(input_wdir, input_wspd)
    npt.assert_equal(type(returned_u), type(ma.masked))
    npt.assert_equal(type(returned_v), type(ma.masked))

def test_vec2comp_default_missing_val_array():
    input_wdir = [0, 90, 180, MISSING]
    input_wspd = [MISSING, 10, 20, 30]
    correct_u = [MISSING, -10, 0, MISSING]
    correct_v= [MISSING, 0, 20, MISSING]
    correct_u = ma.asanyarray(correct_u).astype(np.float64)
    correct_v = ma.asanyarray(correct_v).astype(np.float64)
    correct_u[correct_u == MISSING] = ma.masked
    correct_v[correct_v == MISSING] = ma.masked
    correct_u[correct_v.mask] = ma.masked
    correct_v[correct_u.mask] = ma.masked
    correct_u.set_fill_value(MISSING)
    correct_v.set_fill_value(MISSING)
    returned_u, returned_v = utils.vec2comp(input_wdir, input_wspd)
    npt.assert_almost_equal(returned_u, correct_u)
    npt.assert_almost_equal(returned_v, correct_v)

def test_vec2comp_user_missing_val_single():
    missing = 50
    input_wdir = missing
    input_wspd = 30
    returned_u, returned_v = utils.vec2comp(input_wdir, input_wspd, missing)
    npt.assert_equal(type(returned_u), type(ma.masked))
    npt.assert_equal(type(returned_v), type(ma.masked))

def test_vec2comp_user_missing_val_array():
    missing = 50
    input_wdir = [0, 90, 180, missing]
    input_wspd = [missing, 10, 20, 30]
    correct_u = [missing, -10, 0, missing]
    correct_v= [missing, 0, 20, missing]
    correct_u = ma.asanyarray(correct_u).astype(np.float64)
    correct_v = ma.asanyarray(correct_v).astype(np.float64)
    correct_u[correct_u == missing] = ma.masked
    correct_v[correct_v == missing] = ma.masked
    correct_u[correct_v.mask] = ma.masked
    correct_v[correct_u.mask] = ma.masked
    correct_u.set_fill_value(missing)
    correct_v.set_fill_value(missing)
    returned_u, returned_v = utils.vec2comp(input_wdir, input_wspd, missing)
    npt.assert_almost_equal(returned_u, correct_u)
    npt.assert_almost_equal(returned_v, correct_v)


# comp2vec Tests
def test_comp2vec_single():
    input_u = 5
    input_v = 5
    correct_wdir = 225
    correct_wspd = 7.0710678118654755
    returned_wdir, returned_wspd = utils.comp2vec(input_u, input_v)
    npt.assert_almost_equal(returned_wdir, correct_wdir)
    npt.assert_almost_equal(returned_wspd, correct_wspd)

def test_comp2vec_array():
    input_u = [0, -7.0710678118654746, -15, -14.142135623730951, 0,
        21.213203435596423, 35, 28.284271247461909, 0]
    input_v = [-5, -7.0710678118654746, 0, 14.142135623730951, 25,
        21.213203435596423, 0, -28.284271247461909, -45]
    correct_wdir = [0, 45, 90, 135, 180, 225, 270, 315, 0]
    correct_wspd = [5, 10, 15, 20, 25, 30, 35, 40, 45]
    correct_wdir = np.asanyarray(correct_wdir).astype(np.float64)
    correct_wspd = np.asanyarray(correct_wspd).astype(np.float64)
    returned_wdir, returned_wspd = utils.comp2vec(input_u, input_v)
    npt.assert_almost_equal(correct_wdir, returned_wdir)
    npt.assert_almost_equal(correct_wspd, returned_wspd)

def test_comp2vec_zeros():
    input_u = [0, -20, 0, 40, 0]
    input_v = [-10, 0, 30, 0, -50]
    correct_wdir = [0, 90, 180, 270, 0]
    correct_wspd = [10, 20, 30, 40, 50]
    correct_wdir = np.asanyarray(correct_wdir).astype(np.float64)
    correct_wspd = np.asanyarray(correct_wspd).astype(np.float64)
    returned_wdir, returned_wspd = utils.comp2vec(input_u, input_v)
    npt.assert_equal(returned_wdir, correct_wdir)
    npt.assert_equal(returned_wspd, correct_wspd)

def test_comp2vec_default_missing_val_single():
    input_u = MISSING
    input_v = 30
    returned_wdir, returned_wspd = utils.comp2vec(input_u, input_v)
    npt.assert_equal(type(returned_wdir), type(ma.masked))
    npt.assert_equal(type(returned_wspd), type(ma.masked))

def test_comp2vec_default_missing_val_array():
    input_u = [MISSING, -10, 0, MISSING]
    input_v= [MISSING, 0, 20, MISSING]
    correct_wdir = [0, 90, 180, MISSING]
    correct_wspd = [MISSING, 10, 20, 30]
    correct_wdir = ma.asanyarray(correct_wdir).astype(np.float64)
    correct_wspd = ma.asanyarray(correct_wspd).astype(np.float64)
    correct_wdir[correct_wdir == MISSING] = ma.masked
    correct_wspd[correct_wspd == MISSING] = ma.masked
    correct_wdir[correct_wspd.mask] = ma.masked
    correct_wspd[correct_wdir.mask] = ma.masked
    correct_wdir.set_fill_value(MISSING)
    correct_wspd.set_fill_value(MISSING)
    returned_wdir, returned_wspd = utils.comp2vec(input_u, input_v)
    npt.assert_almost_equal(returned_wdir, correct_wdir)
    npt.assert_almost_equal(returned_wspd, correct_wspd)

def test_comp2vec_user_missing_val_single():
    missing = 50
    input_u = missing
    input_v = 30
    returned_wdir, returned_wspd = utils.vec2comp(input_u, input_v, missing)
    npt.assert_equal(type(returned_wdir), type(ma.masked))
    npt.assert_equal(type(returned_wspd), type(ma.masked))

def test_comp2vec_user_missing_val_array():
    missing = 50
    input_u = [missing, -10, 0, missing]
    input_v= [missing, 0, 20, missing]
    correct_wdir = [0, 90, 180, missing]
    correct_wspd = [missing, 10, 20, 30]
    correct_wdir = ma.asanyarray(correct_wdir).astype(np.float64)
    correct_wspd = ma.asanyarray(correct_wspd).astype(np.float64)
    correct_wdir[correct_wdir == missing] = ma.masked
    correct_wspd[correct_wspd == missing] = ma.masked
    correct_wdir[correct_wspd.mask] = ma.masked
    correct_wspd[correct_wdir.mask] = ma.masked
    correct_wdir.set_fill_value(missing)
    correct_wspd.set_fill_value(missing)
    returned_wdir, returned_wspd = utils.comp2vec(input_u, input_v)
    npt.assert_almost_equal(returned_wdir, correct_wdir)
    npt.assert_almost_equal(returned_wspd, correct_wspd)


# mag Tests
def test_mag_single():
    input_u = 5
    input_v = 5
    correct_answer = np.sqrt(input_u**2 + input_v**2)
    returned_answer = utils.mag(input_u, input_v)
    npt.assert_almost_equal(returned_answer, correct_answer)

def test_mag_zero():
    input_u = 0
    input_v = 0
    correct_answer = 0
    returned_answer = utils.mag(input_u, input_v)
    npt.assert_almost_equal(returned_answer, correct_answer)

def test_mag_array():
    rt2 = np.sqrt(2)
    input_u = [5, 10, 15]
    input_v = [5, 10, 15]
    correct_answer = [5*rt2, 10*rt2, 15*rt2]
    correct_answer = ma.asanyarray(correct_answer)
    returned_answer = utils.mag(input_u, input_v)
    npt.assert_almost_equal(returned_answer, correct_answer)

def test_mag_default_missing_single():
    input_u = MISSING
    input_v = 10
    correct_answer = ma.masked
    returned_answer = utils.mag(input_u, input_v)
    npt.assert_equal(type(returned_answer), type(correct_answer))

def test_mag_default_missing_array():
    rt2 = np.sqrt(2)
    input_u = [MISSING, 10, 20, 30, 40]
    input_v = [0, 10, 20, 30, MISSING]
    correct_answer = [MISSING, 10*rt2, 20*rt2, 30*rt2, MISSING]
    correct_answer = ma.asanyarray(correct_answer).astype(np.float64)
    correct_answer[correct_answer == MISSING] = ma.masked
    returned_answer = utils.mag(input_u, input_v)
    npt.assert_almost_equal(returned_answer, correct_answer)

def test_mag_user_missing_single():
    missing = 50
    input_u = missing
    input_v = 10
    correct_answer = ma.masked
    returned_answer = utils.mag(input_u, input_v, missing)
    npt.assert_equal(type(returned_answer), type(correct_answer))

def test_mag_user_missing_array():
    missing = 50
    rt2 = np.sqrt(2)
    input_u = [missing, 10, 20, 30, 40]
    input_v = [0, 10, 20, 30, missing]
    correct_answer = [missing, 10*rt2, 20*rt2, 30*rt2, missing]
    correct_answer = ma.asanyarray(correct_answer).astype(np.float64)
    correct_answer[correct_answer == missing] = ma.masked
    returned_answer = utils.mag(input_u, input_v, missing)
    npt.assert_almost_equal(returned_answer, correct_answer)
