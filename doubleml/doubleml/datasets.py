import pandas as pd
import numpy as np

from scipy.linalg import toeplitz

from sklearn.datasets import make_spd_matrix


def fetch_401K():
    url = 'https://github.com/VC2015/DMLonGitHub/raw/master/sipp1991.dta'
    data = pd.read_stata(url)
    return data


def fetch_bonus():
    url = 'https://raw.githubusercontent.com/VC2015/DMLonGitHub/master/penn_jae.dat'
    data = pd.read_csv(url, delim_whitespace=True)
    return data


def g(x):
    return np.power(np.sin(x), 2)


def m(x, nu=0., gamma=1.):
    return 0.5/np.pi*(np.sinh(gamma))/(np.cosh(gamma)-np.cos(x-nu))


def m2(x):
    return np.power(x, 2)


def m3(x, nu=0., gamma=1.):
    return 1./np.pi*(np.sinh(gamma))/(np.cosh(gamma)-np.cos(x-nu))


def make_plr_data(n_samples=100, n_features=20, theta=0.5, return_X_y_d=False):
    b = [1 / k for k in range(1, n_features + 1)]
    sigma = make_spd_matrix(n_features)

    X = np.random.multivariate_normal(np.zeros(n_features), sigma, size=[n_samples, ])
    G = g(np.dot(X, b))
    M = m(np.dot(X, b))
    d = M + np.random.standard_normal(size=[n_samples, ])
    y = np.dot(theta, d) + G + np.random.standard_normal(size=[n_samples, ])

    if return_X_y_d:
        return X, y, d
    else:
        x_cols = [f'X{i + 1}' for i in np.arange(n_features)]
        data = pd.DataFrame(np.column_stack((X, y, d)),
                            columns=x_cols + ['y', 'd'])
        return data


def make_pliv_data(n_samples=100, n_features=20, theta=0.5, gamma_z=0.4, return_x_cols=False):
    b = [1/k for k in range(1, n_features+1)]
    sigma = make_spd_matrix(n_features)

    X = np.random.multivariate_normal(np.zeros(n_features), sigma, size=[n_samples, ])
    G = g(np.dot(X, b))
    # instrument
    Z = m(np.dot(X, b)) + np.random.standard_normal(size=[n_samples, ])
    # treatment
    M = m(gamma_z * Z + np.dot(X, b))
    D = M + np.random.standard_normal(size=[n_samples, ])
    Y = np.dot(theta, D) + G + np.random.standard_normal(size=[n_samples, ])

    x_cols = [f'X{i + 1}' for i in np.arange(n_features)]
    data = pd.DataFrame(np.column_stack((X, Y, D, Z)),
                        columns=x_cols + ['y', 'd', 'z'])
    if return_x_cols:
        return data, x_cols

    return data


def make_irm_data(n_samples=100, n_features=20, theta=0.5, return_X_y_d=False):
    b = [1/k for k in range(1, n_features+1)]
    sigma = make_spd_matrix(n_features)

    X = np.random.multivariate_normal(np.zeros(n_features), sigma, size=[n_samples, ])
    G = g(np.dot(X, b))
    M = m3(np.dot(X, b))
    MM = M + np.random.standard_normal(size=[n_samples, ])
    MMM = np.maximum(np.minimum(MM, 0.99), 0.01)
    d = np.random.binomial(p=MMM, n=1)
    y = np.dot(theta, d) + G + np.random.standard_normal(size=[n_samples, ])

    if return_X_y_d:
        return X, y, d
    else:
        x_cols = [f'X{i + 1}' for i in np.arange(n_features)]
        data = pd.DataFrame(np.column_stack((X, y, d)),
                            columns=x_cols + ['y', 'd'])
        return data


def make_iivm_data(n_samples=100, n_features=20, theta=0.5, gamma_z=0.4, return_x_cols=False):
    b = [1/k for k in range(1, n_features+1)]
    sigma = make_spd_matrix(n_features)

    X = np.random.multivariate_normal(np.zeros(n_features), sigma, size=[n_samples, ])
    G = g(np.dot(X, b))
    # instrument
    M1 = m3(np.dot(X, b))
    MM = M1 + np.random.standard_normal(size=[n_samples, ])
    MMM = np.maximum(np.minimum(MM, 0.99), 0.01)
    Z = np.random.binomial(p=MMM, n=1)
    # treatment
    M = m3(gamma_z * Z + np.dot(X, b))
    MM = M + np.random.standard_normal(size=[n_samples, ])
    MMM = np.maximum(np.minimum(MM, 0.99), 0.01)
    D = np.random.binomial(p=MMM, n=1)

    x_cols = [f'X{i + 1}' for i in np.arange(n_features)]
    Y = np.dot(theta, D) + G + np.random.standard_normal(size=[n_samples, ])
    data = pd.DataFrame(np.column_stack((X, Y, D, Z)),
                        columns=x_cols + ['y', 'd', 'z'])
    if return_x_cols:
        return data, x_cols

    return data


def make_pliv_multiway_cluster_data(N, M, dim_X, **kwargs):
    # additional parameters specifiable via kwargs
    theta_0 = kwargs.get('theta_0', 1.0)
    pi_10 = kwargs.get('pi_10', 1.0)

    xx = np.arange(1, dim_X + 1)
    zeta_0 = kwargs.get('zeta_0', np.power(0.5, xx))
    pi_20 = kwargs.get('pi_20', np.power(0.5, xx))
    xi_0 = kwargs.get('xi_0', np.power(0.5, xx))

    omega_X = kwargs.get('omega_X', np.array([0.25, 0.5]))
    omega_eps = kwargs.get('omega_eps', np.array([0.25, 0.5]))
    omega_v = kwargs.get('omega_v', np.array([0.25, 0.5]))
    omega_V = kwargs.get('omega_V', np.array([0.25, 0.5]))

    s_X = kwargs.get('s_X', 0.25)
    s_epsv = kwargs.get('s_epsv', 0.25)

    # use np.tile() and np.repeat() for repeating vectors in different styles, i.e.,
    # np.tile([v1, v2, v3], 2) [v1, v2, v3, v1, v2, v3]
    # np.repeat([v1, v2, v3], 2) [v1, v1, v2, v2, v3, v3]

    alpha_V = np.random.normal(size=(N * M))
    alpha_V_i = np.repeat(np.random.normal(size=N), M)
    alpha_V_j = np.tile(np.random.normal(size=M), N)

    cov_mat = np.array([[1, s_epsv], [s_epsv, 1]])
    alpha_eps_v = np.random.multivariate_normal(np.zeros(2), cov_mat, size=[N * M, ])
    alpha_eps = alpha_eps_v[:, 0]
    alpha_v = alpha_eps_v[:, 1]

    alpha_eps_v_i = np.random.multivariate_normal(np.zeros(2), cov_mat, size=[N, ])
    alpha_eps_i = np.repeat(alpha_eps_v_i[:, 0], M)
    alpha_v_i = np.repeat(alpha_eps_v_i[:, 1], M)

    alpha_eps_v_j = np.random.multivariate_normal(np.zeros(2), cov_mat, size=[M, ])
    alpha_eps_j = np.tile(alpha_eps_v_j[:, 0], N)
    alpha_v_j = np.tile(alpha_eps_v_j[:, 1], N)

    cov_mat = toeplitz([np.power(s_X, k) for k in range(dim_X)])
    alpha_X = np.random.multivariate_normal(np.zeros(dim_X), cov_mat, size=[N * M, ])
    alpha_X_i = np.repeat(np.random.multivariate_normal(np.zeros(dim_X), cov_mat, size=[N, ]),
                          M, axis=0)
    alpha_X_j = np.tile(np.random.multivariate_normal(np.zeros(dim_X), cov_mat, size=[M, ]),
                        (N, 1))

    # generate variables
    X = (1 - omega_X[0] - omega_X[1]) * alpha_X \
        + omega_X[0] * alpha_X_i + omega_X[1] * alpha_X_j

    eps = (1 - omega_eps[0] - omega_eps[1]) * alpha_eps \
          + omega_eps[0] * alpha_eps_i + omega_eps[1] * alpha_eps_j

    v = (1 - omega_v[0] - omega_v[1]) * alpha_v \
        + omega_v[0] * alpha_v_i + omega_v[1] * alpha_v_j

    V = (1 - omega_V[0] - omega_V[1]) * alpha_V \
        + omega_V[0] * alpha_V_i + omega_V[1] * alpha_V_j

    Z = np.matmul(X, xi_0) + V
    D = Z * pi_10 + np.matmul(X, pi_20) + v
    Y = D * theta_0 + np.matmul(X, zeta_0) + eps

    ind = pd.MultiIndex.from_product([range(N), range(M)])
    cols = ['Y', 'D', 'Z', 'V'] + [f'x{i + 1}' for i in np.arange(dim_X)]

    data = pd.DataFrame(np.column_stack((Y, D, Z, V, X)),
                        columns=cols,
                        index=ind)

    return data