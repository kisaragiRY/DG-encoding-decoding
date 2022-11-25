from dataclasses import dataclass
from typing import Union
from copy import deepcopy
from itertools import product
from sklearn.model_selection import TimeSeriesSplit
import numpy as np

from modules.metrics import get_scorer
from modules.decoder import RidgeRegression
from ._split import RollingOriginSplit

@dataclass
class SearchCV:
    """Find the best params with cross validation."""
    estimator: RidgeRegression
    scoring: str
    candidate_params: list
    n_split : int

    def __post_init__(self) -> None:
        """Post processing."""
        self.scorer = get_scorer(self.scoring)
        self.cv = RollingOriginSplit(self.n_split)

    def fit_and_score(self, X, y, train_indexes, test_indexes, hyper_param) -> dict:
        """Fit estimator and compute scores for a given dataset split."""
        X_train, X_test = X[train_indexes], X[test_indexes]
        y_train, y_test = y[train_indexes], y[test_indexes]

        estimator = deepcopy(self.estimator)

        estimator.fit(X_train,y_train, hyper_param)
        fitted_param = estimator.fitted_param

        estimator.predict(X_test)
        y_pred = estimator.prediction

        result = {
            "train_scores": self.scorer(y_train, np.einsum("ij,j->i",X_train, fitted_param)),
            "test_scores" : self.scorer(y_test, y_pred),
            "fitted_param": fitted_param,
        }

        return result
    
    def evaluate_candidates(self, X, y):
        """Run search among cv splits and get the best parameters."""
        self.results = dict()
        min_score = np.inf
        for id_, param, (train_indexes, test_indexes) in enumerate(product(self.candidate_params,self.cv.split(X))):
            result = self.fit_and_score(X, y, train_indexes, test_indexes, param)

            self.results[id_] = {
                "fit_and_score": result,
                "hyper_param": param,
                }
            if result["test_scores"] <= min_score:
                min_score = result["test_scores"]
                self.best_result = self.results[id_]
                