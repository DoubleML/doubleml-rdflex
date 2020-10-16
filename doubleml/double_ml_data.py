import numpy as np
import pandas as pd
import io

from ._helper import assure_2d_array


class DoubleMLData:
    """
    Double machine learning data-backend

    :class:`DoubleMLData` objects can be initialized from
    :class:`pandas.DataFrame`'s as well as :class:`numpy.ndarray`'s.

    Parameters
    ----------
    data : :class:`pandas.DataFrame`
        The data.

    y_col : str
        The outcome variable.

    d_cols : str or list
        The treatment variable(s).

    x_cols : None, str or list
        The covariates.
        If ``None``, all variables (columns of ``data``) which are neither specified as outcome variable ``y_col``, nor
        treatment variables ``d_cols``, nor instrument variables ``z_cols`` are used as covariates.
        Default is ``None``.

    z_cols : None, str or list
        The instrument variable(s).
        Default is ``None``.

    use_other_treat_as_covariate : bool
        Indicates whether in the multiple-treatment case the other treatment variables should be added as covariates.
        Default is ``True``.

    Examples
    --------
    >>> import numpy as np
    >>> from doubleml import DoubleMLData
    >>> from doubleml.datasets import make_plr_CCDDHNR2018
    >>> # initialization from pandas.DataFrame
    >>> np.random.seed(3141)
    >>> df = make_plr_CCDDHNR2018(return_type='DataFrame')
    >>> obj_dml_data_from_df = DoubleMLData(df, 'y', 'd')
    >>> # initialization from np.ndarray
    >>> np.random.seed(3141)
    >>> (x, y, d) = make_plr_CCDDHNR2018(return_type='array')
    >>> obj_dml_data_from_array = DoubleMLData.from_arrays(x, y, d)
    """
    def __init__(self,
                 data,
                 y_col,
                 d_cols,
                 x_cols=None,
                 z_cols=None,
                 use_other_treat_as_covariate=True):
        self.data = data
        self.y_col = y_col
        self.d_cols = d_cols
        self.z_cols = z_cols
        self.use_other_treat_as_covariate = use_other_treat_as_covariate
        if x_cols is not None:
            self.x_cols = x_cols
        else:
            # x_cols defaults to all columns but y_col, d_cols and z_cols
            if self.z_cols is not None:
                y_d_z = set.union(set(self.y_col), set(self.d_cols), set(self.z_cols))
                self.x_cols = [col for col in self.data.columns if col not in y_d_z]
            else:
                y_d = set.union(set(self.y_col), set(self.d_cols))
                self.x_cols = [col for col in self.data.columns if col not in y_d]
        self._set_y_z()
        # by default, we initialize to the first treatment variable
        self._set_x_d(self.d_cols[0])

    def __repr__(self):
        buf = io.StringIO()
        self.data.info(verbose=False, buf=buf)
        data_info = buf.getvalue()
        return f'=== DoubleMLData Object ===\n' \
               f'y_col: {self.y_col}\n' \
               f'd_cols: {self.d_cols}\n' \
               f'x_cols: {self.x_cols}\n' \
               f'z_cols: {self.z_cols}\n' \
               f'data:\n {data_info}'

    @classmethod
    def from_arrays(cls, X, y, d, z=None, use_other_treat_as_covariate=True):
        """
        Initialize :class:`DoubleMLData` from :class:`numpy.ndarray`'s.

        Parameters
        ----------
        X : :class:`numpy.ndarray`
            Array of covariates.

        y : :class:`numpy.ndarray`
            Array of the outcome variable.

        d : :class:`numpy.ndarray`
            Array of treatment variables.

        z : :class:`numpy.ndarray` or None
            Array of instrument variables.
            Default is ``None``.

        use_other_treat_as_covariate : bool
            Indicates whether in the multiple-treatment case the other treatment variables should be added as covariates.
            Default is ``True``.

        Examples
        --------
        >>> import numpy as np
        >>> from doubleml import DoubleMLData
        >>> from doubleml.datasets import make_plr_CCDDHNR2018
        >>> np.random.seed(3141)
        >>> (x, y, d) = make_plr_CCDDHNR2018(return_type='array')
        >>> obj_dml_data_from_array = DoubleMLData.from_arrays(x, y, d)
        """
        X = assure_2d_array(X)
        d = assure_2d_array(d)

        # assert single y variable here
        y_col = 'y'
        if z is None:
            z_cols = None
        else:
            if z.shape[1] == 1:
                z_cols = ['z']
            else:
                z_cols = [f'z{i + 1}' for i in np.arange(z.shape[1])]

        if d.shape[1] == 1:
            d_cols = ['d']
        else:
            d_cols = [f'd{i+1}' for i in np.arange(d.shape[1])]

        x_cols = [f'X{i+1}' for i in np.arange(X.shape[1])]

        if z is None:
            data = pd.DataFrame(np.column_stack((X, y, d)),
                                columns=x_cols + [y_col] + d_cols)
        else:
            data = pd.DataFrame(np.column_stack((X, y, d, z)),
                                columns=x_cols + [y_col] + d_cols + z_cols)

        return cls(data, y_col, d_cols, x_cols, z_cols, use_other_treat_as_covariate)

    @property
    def x(self):
        """
        Array of covariates;
        Dynamic! May depend on the currently set treatment variable;
        To get an array of all covariates (independent of the currently set treatment variable)
        call ``obj.data[obj.x_cols].values``.
        """
        return self._X.values
    
    @property
    def y(self):
        """
        Array of outcome variable.
        """
        return self._y.values
    
    @property
    def d(self):
        """
        Array of treatment variable;
        Dynamic! Depends on the currently set treatment variable;
        To get an array of all treatment variables (independent of the currently set treatment variable)
        call ``obj.data[obj.d_cols].values``.
        """
        return self._d.values
    
    @property
    def z(self):
        """
        Array of instrument variables.
        """
        if self.z_cols is not None:
            return self._z.values
        else:
            return None
    
    @property 
    def all_variables(self):
        """
        All variables available in the dataset.
        """
        return self.data.columns
    
    @property 
    def n_treat(self):
        """
        The number of treatment variables.
        """
        return len(self.d_cols)

    @property
    def n_instr(self):
        """
        The number of instrument variables.
        """
        return len(self.z_cols)
    
    @property 
    def n_obs(self):
        """
        The number of observations.
        """
        return self.data.shape[0]
    
    @property
    def x_cols(self):
        """
        The covariates.
        """
        return self._x_cols
    
    @x_cols.setter
    def x_cols(self, value):
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            raise TypeError('x_cols must be a list')
        assert set(value).issubset(set(self.all_variables))
        self._x_cols = value
    
    @property
    def d_cols(self):
        """
        The treatment variable(s).
        """
        return self._d_cols
    
    @d_cols.setter
    def d_cols(self, value):
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            raise TypeError('d_cols must be a list')
        assert set(value).issubset(set(self.all_variables))
        self._d_cols = value
    
    @property
    def y_col(self):
        """
        The outcome variable.
        """
        return self._y_col
    
    @y_col.setter
    def y_col(self, value):
        assert isinstance(value, str)
        assert value in self.all_variables
        self._y_col = value
    
    @property
    def z_cols(self):
        """
        The instrument variable(s).
        """
        return self._z_cols
    
    @z_cols.setter
    def z_cols(self, value):
        if value is not None:
            if isinstance(value, str):
                value = [value]
            if not isinstance(value, list):
                raise TypeError('z_cols must be a list')
            assert set(value).issubset(set(self.all_variables))
            self._z_cols = value
        else:
            self._z_cols = None
    
    def _set_y_z(self):
        self._y = self.data.loc[:, self.y_col]
        if self.z_cols is None:
            self._z = None
        else:
            self._z = self.data.loc[:, self.z_cols]
    
    def _set_x_d(self, treatment_var):
        assert treatment_var in self.d_cols
        if self.use_other_treat_as_covariate:
            xd_list = self.x_cols + self.d_cols
            xd_list.remove(treatment_var)
        else:
            xd_list = self.x_cols
        self._d = self.data.loc[:, treatment_var]
        self._X = self.data.loc[:, xd_list]
