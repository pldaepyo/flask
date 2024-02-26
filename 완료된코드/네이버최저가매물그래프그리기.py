import pandas as pd
import glob
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def convert_price(prc_str):
    parts = prc_str.replace('억', '').split()
    if len(parts) == 2:
        return int(parts[0]) * 10000 + int(parts[1].replace(',', ''))
    elif len(parts) == 1 and prc_str.endswith('억'):
        return int(parts[0]) * 10000
    return int(prc_str.replace(',', ''))

def get_apartment_data(file_paths):
    all_data = pd.DataFrame()
    for file_path in file_paths:
        df = pd.read_excel(file_path)
        df_filtered = df[['atclNm', 'cfmYmd', 'prcInfo', 'tradTpNm']]
        df_filtered['prcInfo'] = df_filtered['prcInfo'].apply(convert_price)
        all_data = pd.concat([all_data, df_filtered], ignore_index=True)
    return all_data

def select_apartment(apartment_names):
    while True:
        print("\n0. 종료")
        for i, name in enumerate(apartment_names, start=1):
            print(f"{i}. {name}")
        selected_index = input("위 목록에서 아파트 번호를 선택해주세요 (종료는 0): ")
        if selected_index.isdigit():
            selected_index = int(selected_index)
            if selected_index == 0:
                return None
            if 1 <= selected_index <= len(apartment_names):
                return apartment_names[selected_index - 1]
        print("올바른 번호를 입력해주세요.")

def select_trade_type():
    trade_types = ['매매', '전세']
    print("\n1. 매매\n2. 전세")
    while True:
        selected_trade_type_index = input("매매 또는 전세 중 선택해주세요 (1 또는 2): ")
        if selected_trade_type_index.isdigit():
            selected_trade_type_index = int(selected_trade_type_index)
            if 1 <= selected_trade_type_index <= len(trade_types):
                return trade_types[selected_trade_type_index - 1]
        print("올바른 번호를 입력해주세요.")

def plot_graph(filtered_data, selected_apartment_name, selected_trade_type):
    font_path = 'C:\\Windows\\Fonts\\NanumGothic-Regular.ttf'
    font_name = fm.FontProperties(fname=font_path).get_name()
    plt.rc('font', family=font_name)

    plt.figure(figsize=(10, 6))
    plt.plot(filtered_data['cfmYmd'], filtered_data['prcInfo'], marker='o')
    plt.xlabel('cfmYmd')
    plt.ylabel('prcInfo')
    plt.title(f'{selected_apartment_name} - {selected_trade_type} - 날짜별 최저 가격')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    save_directory = 'C:\\Users\\beginplace2\\Desktop\\TEST\\test'
    file_paths = glob.glob(f"{save_directory}/*.xlsx")
    all_data = get_apartment_data(file_paths)
    apartment_names = all_data['atclNm'].unique().tolist()

    while True:
        selected_apartment_name = select_apartment(apartment_names)
        if not selected_apartment_name:
            print("프로그램을 종료합니다.")
            break
        
        selected_trade_type = select_trade_type()
        filtered_data = all_data[(all_data['atclNm'] == selected_apartment_name) & 
                                 (all_data['tradTpNm'] == selected_trade_type)]
        min_price_per_date = filtered_data.groupby('cfmYmd')['prcInfo'].min().reset_index()

        plot_graph(min_price_per_date, selected_apartment_name, selected_trade_type)

if __name__ == "__main__":
    main()