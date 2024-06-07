from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler


def train_data(df: DataFrame):
    df = df.dropna()
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    scaler = MinMaxScaler()
    scaler.fit(X.values)
    X = scaler.transform(X.values)

    model = LinearRegression()
    model.fit(X, y)

    return model, scaler
