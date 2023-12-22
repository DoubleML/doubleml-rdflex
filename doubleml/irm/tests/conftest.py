import numpy as np
import pandas as pd

import pytest

from sklearn.datasets import make_spd_matrix
from sklearn.datasets import make_regression, make_classification

from doubleml.datasets import make_plr_turrell2018, make_irm_data


def _g(x):
    return np.power(np.sin(x), 2)


@pytest.fixture(scope='session',
                params=[(500, 10),
                        (1000, 20),
                        (1000, 100)])
def generate_data_irm(request):
    n_p = request.param
    np.random.seed(1111)
    # setting parameters
    n = n_p[0]
    p = n_p[1]
    theta = 0.5

    # generating data
    data = make_irm_data(n, p, theta, return_type='array')

    return data


@pytest.fixture(scope='session',
                params=[(500, 10),
                        (1000, 20),
                        (1000, 100)])
def generate_data_irm_binary(request):
    n_p = request.param
    np.random.seed(1111)
    # setting parameters
    n = n_p[0]
    p = n_p[1]
    theta = 0.5
    b = [1 / k for k in range(1, p + 1)]
    sigma = make_spd_matrix(p)

    # generating data
    x = np.random.multivariate_normal(np.zeros(p), sigma, size=[n, ])
    G = _g(np.dot(x, b))
    pr = 1 / (1 + np.exp((-1) * (x[:, 0] * (-0.5) + x[:, 1] * 0.5 + np.random.standard_normal(size=[n, ]))))
    d = np.random.binomial(p=pr, n=1, size=[n, ])
    err = np.random.standard_normal(n)

    pry = 1 / (1 + np.exp((-1) * theta * d + G + err))
    y = np.random.binomial(p=pry, n=1, size=[n, ])

    return x, y, d


@pytest.fixture(scope='session',
                params=[(500, 10),
                        (1000, 20)])
def generate_data_irm_w_missings(request):
    n_p = request.param
    np.random.seed(1111)
    # setting parameters
    n = n_p[0]
    p = n_p[1]
    theta = 0.5

    # generating data
    (x, y, d) = make_irm_data(n, p, theta, return_type='array')

    # randomly set some entries to np.nan
    ind = np.random.choice(np.arange(x.size), replace=False,
                           size=int(x.size * 0.05))
    x[np.unravel_index(ind, x.shape)] = np.nan
    data = (x, y, d)

    return data


@pytest.fixture(scope='session',
                params=[(500, 5),
                        (1000, 10)])
def generate_data_quantiles(request):
    n_p = request.param
    np.random.seed(1111)

    # setting parameters
    n = n_p[0]
    p = n_p[1]

    def f_loc(D, X):
        loc = 2 * D
        return loc

    def f_scale(D, X):
        scale = np.sqrt(0.5 * D + 1)
        return scale

    d = (np.random.normal(size=n) > 0) * 1.0
    x = np.random.uniform(0, 1, size=[n, p])
    epsilon = np.random.normal(size=n)

    y = f_loc(d, x) + f_scale(d, x) * epsilon
    data = (x, y, d)

    return data


@pytest.fixture(scope='session',
                params=[(5000, 5),
                        (10000, 10)])
def generate_data_local_quantiles(request):
    n_p = request.param
    np.random.seed(1111)

    # setting parameters
    n = n_p[0]
    p = n_p[1]

    def f_loc(D, X, X_conf):
        loc = 2 * D
        return loc

    def f_scale(D, X, X_conf):
        scale = np.sqrt(0.5 * D + 1)
        return scale

    def generate_treatment(Z, X, X_conf):
        eta = np.random.normal(size=len(Z))
        d = ((1.5 * Z + eta) > 0) * 1.0
        return d

    x = np.random.uniform(0, 1, size=[n, p])
    x_conf = np.random.uniform(-1, 1, size=[n, 4])
    z = np.random.binomial(1, p=0.5, size=n)
    d = generate_treatment(z, x, x_conf)
    epsilon = np.random.normal(size=n)

    y = f_loc(d, x, x_conf) + f_scale(d, x, x_conf)*epsilon
    data = (x, y, d, z)

    return data
