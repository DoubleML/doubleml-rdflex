import pytest
import pandas as pd
import numpy as np

from doubleml import DoubleMLData
from doubleml.rdd import RDFlex

from rdrobust import rdrobust
from sklearn.dummy import DummyRegressor, DummyClassifier


ml_g_dummy = DummyRegressor(strategy='constant', constant=0)
ml_m_dummy = DummyClassifier(strategy='constant', constant=0)


@pytest.fixture(scope='module',
                params=[-0.2, 0.0, 0.4])
def cutoff(request):
    return request.param


@pytest.fixture(scope='module',
                params=[1, 2])
def p(request):
    return request.param


@pytest.fixture(scope='module')
def data(rdd_sharp_data):
    return rdd_sharp_data


@pytest.fixture(scope='module')
def rdd_zero_predictions_fixture(cutoff, p, data):
    kwargs = {
        'p': p
    }

    # set the treatment indicator correctly based on the cutoff
    data['d'] = (data['score'] >= cutoff).astype(bool)
    dml_data = DoubleMLData(data, y_col='y', d_cols='d', s_col='score')

    dml_rdflex = RDFlex(
        dml_data,
        ml_g=ml_g_dummy,
        ml_m=ml_m_dummy,
        cutoff=cutoff,
        **kwargs)
    dml_rdflex.fit(n_iterations=1)

    rdrobust_model = rdrobust(y=data['y'], x=data['score'], c=cutoff, **kwargs)

    res_dict = {
        'dml_rdflex': dml_rdflex,
        'dml_coef': dml_rdflex.coef,
        'dml_se': dml_rdflex.se,
        'rdrobust_model': rdrobust_model,
        'rdrobust_coef': rdrobust_model.coef.values.flatten(),
        'rdrobust_se': rdrobust_model.se.values.flatten()
    }
    return res_dict


@pytest.mark.ci
def test_rdd_coef(rdd_zero_predictions_fixture):
    dml_coef = rdd_zero_predictions_fixture['dml_coef']
    rdrobust_coef = rdd_zero_predictions_fixture['rdrobust_coef']

    assert np.allclose(dml_coef, rdrobust_coef, rtol=1e-9, atol=1e-4)


@pytest.mark.ci
def test_rdd_se(rdd_zero_predictions_fixture):
    dml_se = rdd_zero_predictions_fixture['dml_se']
    rdrobust_se = rdd_zero_predictions_fixture['rdrobust_se']

    assert np.allclose(dml_se, rdrobust_se, rtol=1e-9, atol=1e-4)


# TODO: Failure message right of cutoff is not treated
# TODO: Warning message if fuzzy=False and data is fuzzy
# TODO: Dataset with different cutoffs (dataste cutoff == given cutoff)
# TODO: Placebo test (Dataset cutoff != given cuttoff)

