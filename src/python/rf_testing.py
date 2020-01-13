import pandas as pd
import numpy as np

no_vars = 1000
tau = 5
theta = 20
k_cross_fold_splits = 5
seed = 12345
no_bins = 5

x_var = np.random.normal(100, 10, no_vars)
error_var = np.random.normal(0, 1, no_vars)
ads = pd.DataFrame({'x_var': x_var[0:], 'error_var': error_var[0:]})
ads['y_var'] = tau + theta * ads['x_var'] + ads['error_var']
#
# def group_in_x(x):
#     if 0 < x <= 10:
#         return 1
#     elif 10 < x <= 30:
#         return 2
#     elif 30 < x <= 50:
#         return 3
#     elif 50 < x <= 80:
#         return 4
#     return 5
# ads['x_var_cat'] = ads['x_var'].apply(group_in_x)

ads['x_var_cat'] = pd.Series(pd.qcut(ads['x_var'], q=no_bins, labels=False, retbins=False, precision=3, duplicates='drop'))

summary = {
    'x_var': {
        'count_x': 'count',
        'average_x': 'mean',
        'med_x': 'median',
        'std_x': 'std',
        'max_x': 'max',
        'min_x': 'min'
    }
}

ads.groupby('x_var_cat').agg(summary)

from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import KFold, cross_validate, train_test_split
from statistics import mean

X, y = ads.drop(['y_var', 'error_var'], axis=1).reset_index(drop=True), ads.y_var
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=seed)

X_only, y = ads.drop(['y_var', 'x_var_cat', 'error_var'], axis=1).reset_index(drop=True), ads.y_var
X_only_train, X_only_test, y_only_train, y_only_test = train_test_split(X_only, y, test_size=0.25, random_state=seed)

models= []
models.append(("RF", RandomForestRegressor(n_estimators=100, criterion='mse', min_samples_leaf=2, bootstrap=True, random_state=seed)))
models.append(("SVR", SVR(kernel='rbf', gamma='scale')))
models.append(("GBM", GradientBoostingRegressor(loss='lad', n_estimators=100, criterion='friedman_mse', min_samples_leaf=2, random_state=seed)))

for name, model in models:
    k_fold = KFold(n_splits=k_cross_fold_splits, random_state=seed)
    # cv_result = cross_val_predict(model, X_train, y_train, cv=k_fold, method="predict")
    cv_result = cross_validate(model, X_train, y_train, cv=k_fold, scoring=('r2', 'neg_mean_squared_error'),  return_train_score=True)
    cv_result_only = cross_validate(model, X_only_train, y_only_train, cv=k_fold, scoring=('r2', 'neg_mean_squared_error'), return_train_score=True)
    print(name,
          "\n Test R2 (With X Cat Var): ", -round(mean(cv_result['test_r2']), 5),
          "\n Test R2 (Without X Cat Var): ", -round(mean(cv_result_only['test_r2']), 5),
          "\n Train R2 (With X Cat Var): ", -round(mean(cv_result['train_r2']), 5),
          "\n Train R2 (Without X Cat Var): ", -round(mean(cv_result_only['train_r2']), 5))
