from flask import Flask, request, jsonify
import pandas as pd
import glob
import os

app = Flask(__name__)

def convert_price(prc_str):
    parts = prc_str.replace('억', '').split()
    if len(parts) == 2:
        return int(parts[0]) * 10000 + int(parts[1].replace(',', ''))
    elif len(parts) == 1 and prc_str.endswith('억'):
        return int(parts[0]) * 10000
    return int(prc_str.replace(',', ''))

def get_apartment_data(directory):
    all_data = pd.DataFrame()
    file_paths = glob.glob(f"{directory}/*.xlsx")
    for file_path in file_paths:
        df = pd.read_excel(file_path)
        df_filtered = df[['atclNm', 'cfmYmd', 'prcInfo', 'tradTpNm']]
        df_filtered['prcInfo'] = df_filtered['prcInfo'].apply(convert_price)
        all_data = pd.concat([all_data, df_filtered], ignore_index=True)
    return all_data

@app.route('/apartments', methods=['GET'])
def list_apartments():
    directory = request.args.get('directory')
    if not directory:
        return jsonify({'error': 'Directory parameter is missing'}), 400
    all_data = get_apartment_data(directory)
    apartment_names = all_data['atclNm'].unique().tolist()
    return jsonify(apartment_names)

@app.route('/data', methods=['POST'])
def get_data():
    content = request.json
    directory = content['directory']
    selected_apartment_name = content['selected_apartment_name']
    selected_trade_type = content['selected_trade_type']
    all_data = get_apartment_data(directory)
    filtered_data = all_data[(all_data['atclNm'] == selected_apartment_name) & 
                             (all_data['tradTpNm'] == selected_trade_type)]
    min_price_per_date = filtered_data.groupby('cfmYmd')['prcInfo'].min().reset_index()
    result = min_price_per_date.to_dict('records')
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)