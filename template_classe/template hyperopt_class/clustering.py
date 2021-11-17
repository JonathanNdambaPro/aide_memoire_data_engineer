import typing as t

from hyperopt import STATUS_OK, Trials, fmin, space_eval, tpe
from sklearn import metrics
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cluster import KMeans
from sklearn.mixture import BayesianGaussianMixture


class KmeansHyperopt(BaseEstimator, TransformerMixin):
    def __init__(self, SPACE: t.Dict, max_evals: int = 1000):
        self.SPACE = SPACE
        self.max_evals = max_evals

    def hyperopt_train_test_(self, params: t.Dict) -> float:
        kmeans = KMeans(**params).fit(self.X)
        labels = kmeans.labels_
        neg_silhouette_score = -metrics.silhouette_score(
            self.X, labels, metric="euclidean"
        )
        return neg_silhouette_score

    def f_(self, params: t.Dict):
        neg_silhouette_score = self.hyperopt_train_test_(params)
        return {"loss": neg_silhouette_score, "status": STATUS_OK}

    def find_best_param_(self, trials) -> t.Dict:
        best = fmin(
            self.f_,
            self.SPACE,
            algo=tpe.suggest,
            max_evals=self.max_evals,
            trials=trials,
        )
        return best

    def fit(self, X_, y=None):
        return self

    def transform(self, X_, y=None):
        self.X = X_.copy()
        trials = Trials()
        best = self.find_best_param_(trials)
        beast_kmeans = space_eval(self.SPACE, best)
        kmeans = KMeans(**beast_kmeans).fit(self.X)
        labels = kmeans.labels_
        self.X["kmeans_labels"] = labels

        return self.X


class BayesianGaussianMixtureHyperot(BaseEstimator, TransformerMixin):
    def __init__(self, SPACE: t.Dict, max_evals: int = 1000):
        self.SPACE = SPACE
        self.max_evals = max_evals

    def hyperopt_train_test_(self, params: t.Dict) -> float:
        gmm = BayesianGaussianMixture(**params).fit(self.X)
        neg_log_vraisemblance = -gmm.score(self.X)
        return neg_log_vraisemblance

    def f_(self, params: t.Dict) -> t.Dict:
        neg_log_vraisemblance = self.hyperopt_train_test_(params)
        return {"loss": neg_log_vraisemblance, "status": STATUS_OK}

    def find_best_param_(self, trials) -> t.Dict:
        best = fmin(
            self.f_,
            self.SPACE,
            algo=tpe.suggest,
            max_evals=self.max_evals,
            trials=trials,
        )
        return best

    def fit(self, X_, y=None):
        return self

    def transform(self, X_, y=None):
        self.X = X_.copy()
        trials = Trials()
        best = self.find_best_param_(trials)
        beast_gmm = space_eval(self.SPACE, best)
        gmm = BayesianGaussianMixture(**beast_gmm).fit(self.X)
        self.X["GMM_labels"] = gmm.predict(self.X)

        return self.X
