import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error
from datetime import datetime
import xgboost as xgb
import utils

color_pal = sns.color_palette()
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['lines.markersize'] = 5

TARGET_TEST_CUTOFF_DATE = '2023-08-09T08:00:00'

def load_and_prepare_data(file_path):
    df = pd.read_csv(file_path)
    df = df.set_index('datetime')
    df.index = pd.to_datetime(df.index)
    return df

def plot_and_save(df, file_path):
    df.plot(style='.', figsize=(15, 5), color=color_pal[0], title='Power')
    plt.savefig(file_path)
    plt.close()

def train_and_predict(df, target_cutoff_date):
    train = df.loc[df.index < target_cutoff_date]
    test = df.loc[df.index >= target_cutoff_date]

    train = utils.create_time_series_features(train)
    test = utils.create_time_series_features(test)

    train['weekofyear'] = train['weekofyear'].astype('int32')
    test['weekofyear'] = test['weekofyear'].astype('int32')

    time_series_features = ['dayofyear', 'hour', 'dayofweek', 'weekofyear', 'quarter', 'month', 'year']
    time_series_target = 'pe'

    X_train = train[time_series_features]
    y_train = train[time_series_target]

    X_test = test[time_series_features]
    y_test = test[time_series_target]

    model = utils.train_xgb_regressor(X_train, y_train, X_test, y_test, use_gpu=False)

    test['prediction'] = model.predict(X_test)
    df = df.merge(test[['prediction']], how='left', left_index=True, right_index=True)

    return df, test

def plot_predictions(df, file_path):
    ax = df[['pe']].plot(figsize=(15, 5))
    df['prediction'].plot(ax=ax, style='.')
    plt.legend(['Ground Truth Data', 'Predictions'])
    plt.title('Actual Past Data and Prediction')
    plt.savefig(file_path)
    plt.close()

def evaluate_model(test):
    score = np.sqrt(mean_squared_error(test['pe'], test['prediction']))
    return score

def main(file_path):
    df = load_and_prepare_data(file_path)
    df, test = train_and_predict(df, TARGET_TEST_CUTOFF_DATE)
    plot_and_save(df, 'static/initial_plot.png')
    plot_predictions(df, 'static/prediction_plot.png')
    score = evaluate_model(test)
    return score
