from dataclasses import dataclass
from functools import cached_property
import numpy as np
from scipy.linalg import inv
from .func import *
from scipy import stats

class RidgeRegression():
    '''A linear guassian ridge model.

    x_t=fitted_param.T・n_t + b_t
    x_t: discretized position
    fitted_param: parameter
    n_t: spikes
    b_t: intercept
    '''
    def __init__(self) -> None:
        pass

    def fit(self,X_train:np.array,y_train:np.array,penalty:float):
        '''Fitting based on training data.
        
        return the fitted coefficients

        Parameter:
        ---------
        X_train: np.array
            train design matrix including one column full of 1 for the intercept
        y_train: np.array
            discretized position from continuous coordinates to discrete value 1,2,3...
        penalty: float
            the penalty added on ridge model
        '''
        self.X_train=X_train
        self.y_train=y_train.ravel()
        self.penalty=penalty

        tmp1=np.einsum("ji,ik->jk",self.X_train.T,self.X_train)
        tmp2=np.einsum("ji,i->j",self.X_train.T,self.y_train)
        try: 
            inv(tmp1+penalty*np.identity(len(tmp1)))
            self.fitted_param = np.einsum("ji,i->j",inv(tmp1+penalty*np.identity(len(tmp1))),tmp2)
            self.fitting=True # indicate whether the fitting is successfully conducted

        except: 
            self.fitting=False
            self.fitted_param= np.array([np.nan]*self.X_train.shape[1])

    def predict(self, X_test: np.array):
        '''Predicting using fitted parameters based on test data.
        
        return the predicted results

        Parameter:
        ---------
        design_matrix_test: np.array
            test design matrix including one column full of 1 for the intercept

        '''
        self.prediction = np.einsum("ji,i->j", X_test, self.fitted_param)
