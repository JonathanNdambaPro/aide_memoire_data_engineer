from abc import ABC, abstractmethod
import typing as t
import arviz as az
import pandas as pd
import pymc3 as pm
import numpy as np
from pydantic import validate_arguments, ValidationError


class AbstractBayesianFramework(ABC):
    """Classe mère abstraite qui sert de Framework pour les classes filles, ne peux pas être instancier"""
    def __init__(
        self,
        mu_biais: t.Union[int, float] = 0,
        std_biais: t.Union[int, float] = 10,
        mu_betas: t.Union[int, float] = 0,
        std_betas: t.Union[int, float] = 1,
        sigma_std: t.Union[int, float] = 10,
        size_sample: int = 100,
    ):
        """
        :parameter:
            mu_biais: int|float
                permet de gerer les nu du intercet
            std_biais: int|float
                permet de gerer l'ecart type du biais
            mu_betas: int|float
                moyenne de la distribution des betas
            std_betas: int|float
                ecart-types des betas
            sigma_std: int|float
                ecart type de sigma
            size_sample: int
                d'itérations pour converger vers paramètres à estimer dans le modèles

        :return:
            None
        """
        self.__mu_biais = mu_biais
        self.__std_biais = std_biais
        self.__mu_betas = mu_betas
        self.__std_betas = std_betas
        self.__sigma_std = sigma_std
        self.size_sample = size_sample
        self.trace = None
        self.model = None

    @property
    def mu_biais(self):
        """rend l'attribut __mu_biais privé pour éviter les erreurs en production, self.__mu_biais => self.mu_biais"""
        return self.__mu_biais

    @property
    def std_biais(self):
        return self.__std_biais 

    @property
    def mu_betas(self):
        return self.__mu_betas    
    
    @property
    def std_betas(self):
        return self.__std_betas 

    @property
    def sigma_std(self):
        return self.__sigma_std

    @abstractmethod
    def inference(self, X: pd.DataFrame, y):
        """Classe a implémenté dans toutes les classe fille sinon erreur"""
        pass

    def get_trace(self, varname: t.Union[str, None] = None):
        if varname is None:
            return pm.traceplot(self.trace)
        else:
            return pm.traceplot(self.trace[varname])

    def get_model(self):
        return self.model

    def get_coefficient(self, varname: t.Union[str, None] = None):
        if varname is None:
            return az.summary(self.trace)
        else:
            return az.summary(self.trace[varname])

    def get_forest_plot(self, varname: t.Union[str, None] = None):
        return az.plot_forest(self.trace)

    def get_prediction(self, sample: int = 200) -> t.Any:
        sample_posterior_predictive = pm.sample_posterior_predictive(
            self.trace, samples=sample, model=self.model, random_seed=2
        )

        return np.mean(sample_posterior_predictive["y_pred"], axis=0)


    def get_rsquarred(self, y, sample: int = 200):
        ppc = pm.sample_posterior_predictive(
            self.trace, samples=sample, model=self.model, random_seed=2
        )
        try:
            return az.r2_score(y.values, ppc["y_pred"])
        except:
            return az.r2_score(y, ppc["y_pred"])



    def plot_trace(self, varname: t.Union[str, None] = None):
        if varname is None:
            return az.plot_trace(self.trace)
        else:
            return az.plot_trace(self.trace[varname])

    def plot_posteriori(self, varname: t.Union[str, None] = None):
        if varname is None:
            return az.plot_posterior(self.trace)
        else:
            return az.plot_posterior(self.trace[varname])

    def plot_model(self):
        return pm.model_to_graphviz(self.model)

    def plot_posterior_prediction(
        self, sample: int = 200, figsize: t.Tuple[int] = (12, 6)
    ):
        ppc = pm.sample_posterior_predictive(
            self.trace, samples=sample, model=self.model, random_seed=2
        )
        data_ppc = az.from_pymc3(trace=self.trace, posterior_predictive=ppc)
        return az.plot_ppc(data_ppc, figsize=figsize, mean=True)


class InferenceBayesianRegression(AbstractBayesianFramework):
    """
    regression point de vu bayesien (utilisation d'apriori pour proteger du peu de donnees,
    generation de distribution de parametre)
    """

    @validate_arguments
    def __init__(
        self,
        mu_biais: t.Union[int, float] = 0,
        std_biais: t.Union[int, float] = 10,
        mu_betas: t.Union[int, float] = 0,
        std_betas: t.Union[int, float] = 1,
        sigma_std: t.Union[int, float] = 10,
        size_sample: t.Union[int, float] = 2000,
    ):
        """contructeur qui grace à validate_arguments permet de checker le types des entrées
                :parameter:
            mu_biais: int|float
                permet de gerer les nu du intercet
            std_biais: int|float
                permet de gerer l'ecart type du biais
            mu_betas: int|float
                moyenne de la distribution des betas
            std_betas: int|float
                ecart-types des betas
            sigma_std: int|float
                ecart type de sigma
            size_sample: int
                d'itérations pour converger vers paramètres à estimer dans le modèles

        :return:
            None
        """
        try:
            super().__init__(
                mu_biais=mu_biais,
                std_biais=std_biais,
                mu_betas=mu_betas,
                std_betas=std_betas,
                sigma_std=sigma_std,
                size_sample=size_sample,
            )
        except ValidationError as exc:
            print(exc)


    def inference(self, X: pd.DataFrame, y):
        """inférence avec comme hypothèse que les betas suivent une loi normale"""
        with pm.Model() as model:
            biais = pm.Normal("biais", mu=self.mu_biais, sd=self.std_biais)
            betas = pm.Normal(
                "betas", mu=self.mu_betas, sd=self.std_betas, shape=X.shape[1]
            )
            sigma = pm.HalfNormal("sigma", sigma=self.sigma_std)
            y_pred = pm.Normal(
                "y_pred", mu=pm.math.dot(X, betas) + biais, sd=sigma, observed=y
            )
            self.trace = pm.sample(self.size_sample)

        self.model = model


class RobustInferenceBayesianRegression(AbstractBayesianFramework):
    """
    Regression resistante aux outliers (maximum de vraisemblance avec student au lieu de gaussian)
    """

    @validate_arguments
    def __init__(
        self,
        mu_biais: t.Union[int, float] = 0,
        std_biais: t.Union[int, float] = 10,
        mu_betas: t.Union[int, float] = 0,
        std_betas: t.Union[int, float] = 1,
        sigma_std: t.Union[int, float] = 10,
        size_sample: t.Union[int, float] = 2000,
        student_nu: t.Union[int, float] = 1 / 30,
    ):
        """
        :parameter:
            student_nu: int|float
                parametre de normalité de la loi de students
        """
        try:
            super().__init__(
                mu_biais=mu_biais,
                std_biais=std_biais,
                mu_betas=mu_betas,
                std_betas=std_betas,
                sigma_std=sigma_std,
                size_sample=size_sample,
            )

            self.__student_nu = student_nu
        except ValidationError as exc:
            print(exc)

    @property
    def student_nu(self):
        return self.__student_nu

    def inference(self, X: pd.DataFrame, y):

        with pm.Model() as model:
            biais = pm.Normal("biais", mu=self.mu_biais, sd=self.std_biais)
            betas = pm.Normal(
                "betas", mu=self.mu_betas, sd=self.std_betas, shape=X.shape[1]
            )
            sigma = pm.HalfNormal("sigma", sigma=self.sigma_std)
            y_pred = pm.StudentT(
                "y_pred",
                mu=pm.math.dot(X, betas) + biais,
                sigma=sigma,
                nu=self.student_nu,
                observed=y,
            )
            self.trace = pm.sample(self.size_sample)

        self.model = model


class RidgeInferenceBayesianRegression(AbstractBayesianFramework):
    @validate_arguments
    def __init__(
        self,
        mu_biais: t.Union[int, float] = 0,
        std_biais: t.Union[int, float] = 10,
        mu_betas: t.Union[int, float] = 0,
        std_betas: t.Union[int, float] = 1,
        sigma_std: t.Union[int, float] = 10,
        size_sample: t.Union[int, float] = 2000,
        coeff_ridge: t.Union[int, float] = 1,
    ):
        try:
            super().__init__(
                mu_biais=mu_biais,
                std_biais=std_biais,
                mu_betas=mu_betas,
                std_betas=std_betas,
                sigma_std=sigma_std,
                size_sample=size_sample,
            )

            self.__coeff_ridge = coeff_ridge
        except ValidationError as exc:
            print(exc)

    @property
    def coeff_ridge(self):
        return self.__coeff_ridge

    def inference(self, X: pd.DataFrame, y):

        with pm.Model() as model:
            sigma_betas = pm.HalfNormal("sigma_betas", sigma=self.coeff_ridge)
            biais = pm.Normal("biais", mu=self.mu_biais, sd=self.std_biais)
            betas = pm.Normal(
                "betas", mu=self.mu_betas, sd=sigma_betas, shape=X.shape[1]
            )
            sigma = pm.HalfNormal("sigma", sigma=self.sigma_std)
            y_pred = pm.Normal(
                "y_pred", mu=pm.math.dot(X, betas) + biais, sd=sigma, observed=y
            )
            self.trace = pm.sample(self.size_sample)

        self.model = model


class RobustRidgeInferenceBayesianRegression(AbstractBayesianFramework):
    @validate_arguments
    def __init__(
        self,
        mu_biais: t.Union[int, float] = 0,
        std_biais: t.Union[int, float] = 10,
        mu_betas: t.Union[int, float] = 0,
        std_betas: t.Union[int, float] = 1,
        sigma_std: t.Union[int, float] = 10,
        size_sample: t.Union[int, float] = 2000,
        student_nu: t.Union[int, float] = 1 / 30,
        coeff_ridge: t.Union[int, float] = 1,
    ):
        try:
            super().__init__(
                mu_biais=mu_biais,
                std_biais=std_biais,
                mu_betas=mu_betas,
                std_betas=std_betas,
                sigma_std=sigma_std,
                size_sample=size_sample,
            )

            self.__student_nu = student_nu
            self.__coeff_ridge = coeff_ridge
        except ValidationError as exc:
            print(exc)

    @property
    def coeff_ridge(self):
        return self.__coeff_ridge

    @property
    def student_nu(self):
        return self.__student_nu

    def inference(self, X: pd.DataFrame, y):

        with pm.Model() as model:
            sigma_betas = pm.HalfNormal("sigma_betas", sigma=self.coeff_ridge)
            biais = pm.Normal("biais", mu=self.mu_biais, sd=self.std_biais)
            betas = pm.Normal(
                "betas", mu=self.mu_betas, sd=sigma_betas, shape=X.shape[1]
            )
            sigma = pm.HalfNormal("sigma", sigma=self.sigma_std)
            y_pred = pm.StudentT(
                "y_pred",
                mu=pm.math.dot(X, betas) + biais,
                sigma=sigma,
                nu=self.student_nu,
                observed=y,
            )
            self.trace = pm.sample(self.size_sample)

        self.model = model


class PositiveInferenceBayesianRegression(AbstractBayesianFramework):
    """
    regression point de vu bayesien (utilisation d'apriori pour proteger du peu de donnees,
    generation de distribution de parametre)
    """

    @validate_arguments
    def __init__(
        self,
        mu_biais: t.Union[int, float] = 0,
        std_biais: t.Union[int, float] = 10,
        mu_betas: t.Union[int, float] = 0,
        std_betas: t.Union[int, float] = 1,
        sigma_std: t.Union[int, float] = 10,
        size_sample: t.Union[int, float] = 100,
    ):
        """
        :parameter:
            mu_biais: int|float
                permet de gerer les nu du intercet
            std_biais; int|float
                permet de gerer l'ecart type du biais
        """
        try:
            super().__init__(
                mu_biais=mu_biais,
                std_biais=std_biais,
                mu_betas=mu_betas,
                std_betas=std_betas,
                sigma_std=sigma_std,
                size_sample=size_sample,
            )

        except ValidationError as exc:
            print(exc)

    def inference(self, X: pd.DataFrame, y):

        with pm.Model() as model:
            biais = pm.Normal("biais", mu=self.mu_biais, sd=self.std_biais)
            betas = pm.HalfNormal("betas", sigma=self.std_betas, shape=X.shape[1])
            sigma = pm.HalfNormal("sigma", sigma=self.sigma_std)
            y_pred = pm.Normal(
                "y_pred", mu=pm.math.dot(X, betas) + biais, sd=sigma, observed=y
            )
            self.trace = pm.sample(self.size_sample)

        self.model = model


class PositiveRobustInferenceBayesianRegression(AbstractBayesianFramework):
    """
    Regression resistante aux outliers (maximum de vraisemblance avec student au lieu de gaussian)
    """

    @validate_arguments
    def __init__(
        self,
        mu_biais: t.Union[int, float] = 0,
        std_biais: t.Union[int, float] = 10,
        mu_betas: t.Union[int, float] = 0,
        std_betas: t.Union[int, float] = 1,
        sigma_std: t.Union[int, float] = 10,
        size_sample: t.Union[int, float] = 2000,
        student_nu: t.Union[int, float] = 1 / 30,
    ):
        try:
            super().__init__(
                mu_biais=mu_biais,
                std_biais=std_biais,
                mu_betas=mu_betas,
                std_betas=std_betas,
                sigma_std=sigma_std,
                size_sample=size_sample,
            )

            self.__student_nu = student_nu
        except ValidationError as exc:
            print(exc)

    @property
    def student_nu(self):
        return self.__student_nu

    def inference(self, X: pd.DataFrame, y):

        with pm.Model() as model:
            biais = pm.Normal("biais", mu=self.mu_biais, sd=self.std_biais)
            betas = pm.HalfNormal("betas", sigma=self.std_betas, shape=X.shape[1])
            sigma = pm.HalfNormal("sigma", sigma=self.sigma_std)
            y_pred = pm.StudentT(
                "y_pred",
                mu=pm.math.dot(X, betas) + biais,
                sigma=sigma,
                nu=self.student_nu,
                observed=y,
            )
            self.trace = pm.sample(self.size_sample)

        self.model = model


class PositiveRidgeInferenceBayesianRegression(AbstractBayesianFramework):
    @validate_arguments
    def __init__(
        self,
        mu_biais: t.Union[int, float] = 0,
        std_biais: t.Union[int, float] = 10,
        mu_betas: t.Union[int, float] = 0,
        std_betas: t.Union[int, float] = 1,
        sigma_std: t.Union[int, float] = 10,
        size_sample: t.Union[int, float] = 2000,
        coeff_ridge: t.Union[int, float] = 1,
    ):
        try:
            super().__init__(
                mu_biais=mu_biais,
                std_biais=std_biais,
                mu_betas=mu_betas,
                std_betas=std_betas,
                sigma_std=sigma_std,
                size_sample=size_sample,
            )

            self.__coeff_ridge = coeff_ridge
        except ValidationError as exc:
            print(exc)

    @property
    def coeff_ridge(self):
        return self.__coeff_ridge

    def inference(self, X: pd.DataFrame, y):

        with pm.Model() as model:
            sigma_betas = pm.HalfNormal("sigma_betas", sigma=self.coeff_ridge)
            biais = pm.Normal("biais", mu=self.mu_biais, sd=self.std_biais)
            betas = pm.HalfNormal("betas", sigma=sigma_betas, shape=X.shape[1])
            sigma = pm.HalfNormal("sigma", sigma=self.sigma_std)
            y_pred = pm.Normal(
                "y_pred", mu=pm.math.dot(X, betas) + biais, sd=sigma, observed=y
            )
            self.trace = pm.sample(self.size_sample)

        self.model = model


class PositiveRobustRidgeInferenceBayesianRegression(AbstractBayesianFramework):
    @validate_arguments
    def __init__(
        self,
        mu_biais: t.Union[int, float] = 0,
        std_biais: t.Union[int, float] = 10,
        mu_betas: t.Union[int, float] = 0,
        std_betas: t.Union[int, float] = 1,
        sigma_std: t.Union[int, float] = 10,
        size_sample: t.Union[int, float] = 2000,
        student_nu: t.Union[int, float] = 1 / 30,
        coeff_ridge: t.Union[int, float] = 1,
    ):
        try:
            super().__init__(
                mu_biais=mu_biais,
                std_biais=std_biais,
                mu_betas=mu_betas,
                std_betas=std_betas,
                sigma_std=sigma_std,
                size_sample=size_sample,
            )

            self.__student_nu = student_nu
            self.__coeff_ridge = coeff_ridge
        except ValidationError as exc:
            print(exc)

    @property
    def coeff_ridge(self):
        return self.__coeff_ridge

    @property
    def student_nu(self):
        return self.__student_nu

    def inference(self, X: pd.DataFrame, y):

        with pm.Model() as model:
            sigma_betas = pm.HalfNormal("sigma_betas", sigma=self.coeff_ridge)
            biais = pm.Normal("biais", mu=self.mu_biais, sd=self.std_biais)
            betas = pm.HalfNormal("betas", sigma=sigma_betas, shape=X.shape[1])
            sigma = pm.HalfNormal("sigma", sigma=self.sigma_std)
            y_pred = pm.StudentT(
                "y_pred",
                mu=pm.math.dot(X, betas) + biais,
                sigma=sigma,
                nu=self.student_nu,
                observed=y,
            )
            self.trace = pm.sample(self.size_sample)

        self.model = model