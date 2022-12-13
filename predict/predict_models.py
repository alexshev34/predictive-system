import pandas as pd

def exponential_smoothing(df):
    months_list = df['month'].to_list()
    values_list = df['value'].to_list()

    predict_list = list()
    prev_value = None

    k = 0.8
    result_forecast = 1

    for i in values_list:
        if prev_value:
            result_forecast = int(k * i + (1 - k) * result_forecast)
            predict_list.append(result_forecast)
            prev_value = i
        else:
            prev_value = i
            result_forecast = int(k * i + (1 - k) * prev_value)

    predicted_dict = {"month":months_list, "value": values_list}
    df = pd.DataFrame(predicted_dict)
    
    return df

def predict_ozon(df):
    predicted_df = exponential_smoothing(df)
    return predicted_df

def predict_wb(df):
    predicted_df = exponential_smoothing(df)
    return predicted_df

def predict_avito(df):
    predicted_df = exponential_smoothing(df)
    return predicted_df

def predict_yandex(df):
    predicted_df = exponential_smoothing(df)
    return predicted_df