from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    # HTML 파일을 렌더링하여 반환
    return render_template('index.html')

@app.route('/get-stock-data/<stock_code>')
def get_stock_data(stock_code):
    try:
        df = pd.read_excel('stock_info.xlsx', sheet_name=stock_code)
        # 여러 셀의 값들을 가져옵니다
        average_self_per = df.iat[16, 0]   # 예를 들어 18행 A열
        average_self_pbr = df.iat[16, 1]  # 예를 들어 18행 B열
        average_self_roe = df.iat[16, 2]  # 예를 들어 18행 C열
        average_section_per = df.iat[18, 0]   # 예를 들어 20행 A열
        average_section_pbr = df.iat[18, 1]  # 예를 들어 20행 B열
        average_section_roe = df.iat[18, 2]  # 예를 들어 20행 C열

        # 적정가격 공식(1) : EPS×업종평균PER
        eps_2024 = int(df.iat[8,4])
        right_price_1 = int(eps_2024*average_section_per)
        print('적정가격_1:', right_price_1, '원')

        # 적정가격 공식(2) : BPS×업종평균PBR
        bps_2024 = int(df.iat[10,4])
        right_price_2 = int(bps_2024*average_section_pbr)
        print('적정가격_2:', right_price_2, '원')
        
        # 적정가격 공식(3) : EPSx(1+0.03)/(ROE-0.03) #대부분 예상 이익 성장률로 3~7%로 본다. -> 0.03 대입
        roe_2024 = float(df.iat[4,4])
        right_price_3 = int( eps_2024 * 1.03 / ((roe_2024/100) - 0.03))

        # 모든 셀 값을 JSON 객체로 반환
        return jsonify({
            'average_self_per': average_self_per,
            'average_self_pbr': average_self_pbr,
            'average_self_roe': average_self_roe,
            'average_section_per': average_section_per,
            'average_section_pbr': average_section_pbr,
            'average_section_roe': average_section_roe,
            'right_price_1': right_price_1,
            'right_price_2': right_price_2,
            'right_price_3': right_price_3
        })
    except Exception as e:
        app.logger.error(f"오류 발생: {e}")
        return jsonify({'error': '서버 내부 오류'}), 500


if __name__ == '__main__':
    app.run(debug=True)
