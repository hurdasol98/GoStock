import requests
from bs4 import BeautifulSoup
import pandas as pd


# 시작 URL 설정
url = "https://finance.naver.com/sise/sise_market_sum.naver"

# 요청 헤더 설정 (필요한 경우)
headers = {'User-Agent': 'Mozilla/5.0'}

# 종목 목록 페이지 가져오기
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Excel 파일 초기화
excel_writer = pd.ExcelWriter('stock_info.xlsx', engine='openpyxl')

# 페이지 번호 부분 파싱하여 최대 페이지 수 얻기
page_area = soup.find('td', class_='pgRR').find('a')['href']
max_page_num = int(page_area.split('=')[-1])

print('!!!크롤링 시작합니다!!!!')

# 모든 페이지에 대해 반복
for page in range(1, max_page_num + 1):
    # 페이지 별 URL 업데이트
    page_url = f"{url}?&page={page}"
    response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 'type_2' 클래스를 가진 table의 tbody 내의 'tltle' 클래스를 가진 a 태그 찾기
    for a_tag in soup.select('table.type_2 tbody tr a.tltle'):
        stock_url = "https://finance.naver.com" + a_tag['href']
        stock_name = a_tag.text  # 종목 이름
        print(stock_name)
        # 각 종목의 상세 페이지로부터 데이터 가져오기
        stock_response = requests.get(stock_url, headers=headers)
        stock_soup = BeautifulSoup(stock_response.text, 'html.parser')

        # 'tb_type1 tb_num tb_type1_ifrs' 클래스를 가진 table의 tbody 찾기
        first_table = stock_soup.find('table', {'class': 'tb_type1 tb_num tb_type1_ifrs'})
        if first_table is None:  # 첫 번째 테이블을 찾지 못한 경우
            continue  # 다음 a_tag로 넘어감
        first_table_body = first_table.find('tbody')

        ## 첫 번째 테이블의 데이터를 DataFrame으로 변환
        rows = []
        for tr in first_table_body.find_all('tr'):
        # 열 제목(<th>)과 데이터(<td>)를 추출하되, 데이터가 비어있으면 '-'로 대체
            cols = [elem.text.strip() if elem.text.strip() != '' else '-' for elem in tr.find_all(['th', 'td'])]
            rows.append(cols)
        # 첫 번째 행을 열 이름으로, 나머지 행을 데이터로 하는 DataFrame 생성
        df = pd.DataFrame(rows[1:], columns=rows[0]).reset_index(drop=True)

        # 'section trade_compare' 클래스를 가진 div 아래의 'tb_type1 tb_num' 클래스를 가진 table 찾기
        section_trade_compare = stock_soup.find('div', {'class': 'section trade_compare'})
        if section_trade_compare is None:  # 해당 섹션을 찾지 못한 경우
            continue  # 다음 a_tag로 넘어감
        second_table = section_trade_compare.find('table', {'class': 'tb_type1 tb_num'})
        if second_table is None:  # 두 번째 테이블을 찾지 못한 경우
            continue  # 다음 a_tag로 넘어감

        ## 두 번째 테이블의 데이터를 DataFrame으로 변환
        # thead에서 첫 번째 'tr'을 찾아 열 제목 추출
        thead_row = second_table.find('thead').find('tr')
        column_titles = []
        for th in thead_row.find_all('th'):
            # 'a' 태그가 있으면 'a' 태그 내의 텍스트를 사용, 그렇지 않으면 'th' 태그의 텍스트를 사용
            a_tag = th.find('a')
            if a_tag:
                column_titles.append(a_tag.get_text(strip=True))
            else:
                column_titles.append(th.get_text(strip=True))

        # 'tbody'에서 데이터 행 추출
        tbody_rows = second_table.find('tbody').find_all('tr')
        data_rows = []
        for tr in tbody_rows:
            cols = [elem.text.strip() if elem.text.strip() != '' else '-' for elem in tr.find_all(['th', 'td'])]
            data_rows.append(cols)
        
        # DataFrame 생성
        second_df = pd.DataFrame(data_rows, columns=column_titles).reset_index(drop=True)

        # DataFrame 합치기
        combined_df = pd.concat([df, second_df], axis=1, sort=False, ignore_index=False).reset_index(drop=True)

        # DataFrame을 excel로 변환 + sheet의 이름을 종목명으로 지정
        combined_df.to_excel(excel_writer, sheet_name=stock_name[:31], index=False)

# Excel 파일 저장
excel_writer.close()

