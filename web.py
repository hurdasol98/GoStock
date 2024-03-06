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
        
        # 모든 셀 값을 JSON 객체로 반환
        return jsonify({
            'average_self_per': average_self_per,
            'average_self_pbr': average_self_pbr,
            'average_self_roe': average_self_roe,
            'average_section_per': average_section_per,
            'average_section_pbr': average_section_pbr,
            'average_section_roe': average_section_roe
        })
    except Exception as e:
        app.logger.error(f"오류 발생: {e}")
        return jsonify({'error': '서버 내부 오류'}), 500


if __name__ == '__main__':
    app.run(debug=True)
