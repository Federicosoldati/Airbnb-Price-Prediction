from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, SimpleImputer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
import numpy as np
import pandas as pd


class KMeansClusterer(BaseEstimator, TransformerMixin):
    
    def __init__(self, n_clusters=2, features_cluster=None, initial_centroids=None):
        self.n_clusters = n_clusters
        self.features_cluster = features_cluster
        self.init_cent = initial_centroids
    
    def fit(self, X, y=None):
        if self.features_cluster is None:
            self.features_cluster = list(X.columns)
        
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            n_init=1,
            init = self.init_cent,
            random_state=1)
        self.kmeans.fit(X[self.features_cluster])
        return self
    
    def transform(self, X, y=None):
        X_new = X.copy()
        X_new['location_zone'] = self.kmeans.predict(X_new[self.features_cluster])
        X_new['location_zone'] = X_new['location_zone'].astype(str)
        X_new.drop(columns=self.features_cluster, inplace=True)
        return X_new
    
class GaussianClusterer(BaseEstimator, TransformerMixin):
    
    def __init__(self, n_clusters=2, features_cluster=None, initial_centroids=None):
        self.n_clusters = n_clusters
        self.features_cluster = features_cluster
        self.initial_centroids = initial_centroids
    
    def fit(self, X, y=None):
        if self.features_cluster is None:
            self.features_cluster = list(X.columns)
        
        self.gaussian = GaussianMixture(
            n_components=self.n_clusters,
            means_init=self.initial_centroids)
        
        self.gaussian.fit(X[self.features_cluster])
        return self
    
    def transform(self, X, y=None):
        X_new = X.copy()
        X_new['location_zone_g'] = self.gaussian.predict(X_new[self.features_cluster])
        X_new['location_zone_g'] = X_new['location_zone_g'].astype(str)
        X_new.drop(columns=self.features_cluster, inplace=True)
        return X_new
    

class PCATransformer(BaseEstimator, TransformerMixin):
    def __init__(self, n_components=2, columns=None):
        self.n_components = n_components
        self.columns = columns
        
    def fit(self, X, y=None):
        if self.columns is None:
            self.columns = list(X.columns)
        
        self.pca = PCA(n_components=self.n_components)
        self.pca.fit(X[self.columns])
        self.comps_cols = ['reviews_comp_'+str(i) for i in range(1,self.n_components+1)]

        return self
    
    def transform(self, X, y=None):
        X_new = X.copy()
        X_new[self.comps_cols] = self.pca.transform(X_new[self.columns])
        X_new.drop(columns=self.columns, inplace=True)
        return X_new


class ColumnDropper(BaseEstimator, TransformerMixin):
    def __init__(self, columns_to_drop):
        self.columns_to_drop = columns_to_drop
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X_new = X.copy()
        X_new.drop(columns=self.columns_to_drop, inplace=True)
        return X_new
    

class MissingFlagger(BaseEstimator, TransformerMixin):
    def __init__(self, columns_to_flag):
        self.columns_to_flag = columns_to_flag
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X_new = X.copy()

        for column in self.columns_to_flag:
            new_col = 'has_missing_'+column
            X_new[new_col] = [
                1 
                if pd.isna(i) 
                else 0 
                for i in X_new[column]
                ]

        X_new.drop(columns=self.columns_to_flag, inplace=True)
        return X_new


class AmenitiesCounter(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X_new = X.copy()
        X_new['count_amenities'] = [
            np.nan 
            if pd.isna(i) 
            else len(i.split(',')) 
            for i in X_new['property_amenities']
            ]
        X_new.drop(columns=['property_amenities'], inplace=True)
        return X_new
    
class HostVerificationsCounter(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X_new = X.copy()
        X_new['count_host_verifications'] = [
            np.nan 
            if pd.isna(i) 
            else len(i.split(',')) 
            for i in X_new['host_verified']
            ]
        X_new.drop(columns=['host_verified'], inplace=True)
        return X_new
    
class ExtrasHandler(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X_new = X.copy()

        list_items = [
            ['host_is_superhost', 'Host Is Superhost'],
            ['is_location_exact', 'Is Location Exact'],
            ['is_instant_bookable', 'Instant Bookable']
            ]

        for item in list_items:
            X_new[item[0]] = [
                0 
                if (pd.isna(i) or item[1] not in i.split(', ')) 
                else 1 
                for i in X_new['extra']
                ]
        
        X_new.drop(columns=['extra'], inplace=True)
        return X_new
    
class PropertyTypeHandler(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X_new = X.copy()

        categories = [
            'Apartment',
            'House',
            'Loft',
            'Bed & Breakfast',
            'Townhouse',
            'Condominium'
            ]

        X_new['property_type_new'] = [
            i 
            if i in categories 
            else 'Other' 
            for i in X_new['property_type']
            ]
        
        X_new.drop(columns=['property_type'], inplace=True)
        return X_new
    
class BookingCancelHandler(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        X_new = X.copy()

        X_new['booking_cancel_policy_new'] = [
            1 
            if 'strict' in i 
            else 0 
            for i in X_new['booking_cancel_policy']
            ]
        
        X_new.drop(columns=['booking_cancel_policy'], inplace=True)
        return X_new

class CustomOneHotEncoder(BaseEstimator, TransformerMixin):
    def __init__(self, columns):
        self.columns = columns
        
    def fit(self, X, y=None):
        cats_to_remove = [
            X[i].value_counts().index[-1] 
            for i in self.columns]
        self.encoder = OneHotEncoder(drop=cats_to_remove)
        self.encoder.fit(X[self.columns])
        return self
        
    def transform(self, X):
        X_new = X.copy()
        feature_names = self.encoder.get_feature_names_out(self.columns)
        X_new[feature_names] = self.encoder.transform(X_new[self.columns]).toarray()
        X_new.drop(columns=self.columns, inplace=True)
        
        return X_new

    
class CustomStandardScaler(BaseEstimator, TransformerMixin):
    def __init__(self, columns=None):
        self.columns = columns

    def fit(self, X, y=None):
        if self.columns is None:
            self.columns = list(X.columns)
        
        self.scaler = StandardScaler()

        self.scaler.fit(X[self.columns])
        return self

    def transform(self, X):
        X_new = X.copy()
        X_temp = X_new[self.columns]
        X_new.drop(columns=self.columns, inplace=True)
        X_new[self.columns] = self.scaler.transform(X_temp)
        return X_new
    
class CustomIterativeImputer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):  
        self.imputer = IterativeImputer()

        self.imputer.fit(X)
        return self

    def transform(self, X):
        X_new = X.copy()
        X_new[list(X.columns)] = self.imputer.transform(X_new)
        return X_new

class CustomSimpleImputer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):  
        self.imputer = SimpleImputer()

        self.imputer.fit(X)
        return self

    def transform(self, X):
        X_new = X.copy()
        X_new[list(X.columns)] = self.imputer.transform(X_new)
        return X_new