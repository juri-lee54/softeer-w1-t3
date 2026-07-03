## 1주차 미션3 3팀 위키
### 1. wikipeida 페이지가 아닌, IMF 홈페이지에서 직접 데이터를 가져오는 방법은 없을까요? 어떻게 하면 될까요?
#### 방법 1 - WEO Database CSV/Excel 다운로드
IMF World Economic Outlook(WEO) 데이터베이스에서 CSV 또는 Excel 파일을 직접 다운로드해서 읽는 방법이다.
```
url = 'https://www.imf.org/~/.../WEO_data.csv'
df = pd.read_csv(url)
```



#### 방법 2 - IMF DataMapper API 사용
- [IMF-API](https://data.imf.org/en/Resource-Pages/IMF-API) 를 사용하여 직접적으로 데이터를 가져올 수 있다.
- 크롤링이 아니기 때문에 안정성이 매우 높다. 웹크롤링의 경우 웹사이트의 구조가 언제든지 바뀔 수 있어, 이에 맞게 코드를 계속 수정해야 한다.
- 속도 또한 직접 크롤링 하는 것이 아니기에 훨씬 빠르다.
- 이번 미션의 GDP 데이터는 IMF World Economic Outlook, WEO 데이터에 해당한다. WEO 데이터베이스는 국가별 거시경제 지표를 제공하며, WEO는 매년 두 차례 진행되는 작업을 통해 4월과 9월/10월 발표로 이어진다. 즉, IMF Data Portal 또는 IMF DataMapper API에서 GDP, current prices 지표를 직접 조회하는 방식으로 Extract 단계를 바꿀 수 있다.
  - IMF API에서 사용 가능한 indicator 목록을 조회한다.
  - GDP, current prices 지표의 indicator code를 찾는다.
  - IMF API에서 국가 목록 또는 지역 목록을 조회한다.
  - GDP 지표와 국가 코드를 조합해 국가별 GDP 데이터를 요청한다.
  - 응답 JSON 데이터를 pandas DataFrame으로 변환한다.
  - 기존 Transform 단계에서 단위 변환, 정렬, 필터링을 수행한다.
```
url = 'https://www.imf.org/external/datamapper/api/v1/NGDPD'
response = requests.get(url)
data = response.json()  # JSON 형태로 GDP 데이터를 받아옴
```

- Wikipedia 스크래핑과 비교했을 때 장단점은 다음과 같다.
<img width="350" height="200" alt="image" src="https://github.com/user-attachments/assets/1a54a133-887a-4e0a-839b-064eb3bb8c36" />

- 데이터 원출처에서 직접 가져오기 때문에 신뢰성이 높고, HTML 구조 변경에 영향을 받지 않는다.
- API 응답에는 연도, 국가 코드, 지표 코드 같은 메타데이터가 포함될 수 있어 데이터 관리와 재사용에도 더 적합하다.
- 단, IMF에서 직접 가져오면 국가명이 IMF 고유 표기 방식(예: “Taiwan Province of China”)으로 되어 있어서 별도 정제가 필요하다.

---
### 2. 만약 데이터가 갱신되면 과거의 데이터는 어떻게 되어야 할까요? 과거의 데이터를 조회하는 게 필요하다면 ETL 프로세스를 어떻게 변경해야 할까요?
지금 코드는 실행할 때마다 과거 데이터가 덮어써져 사라진다.

하지만 GDP 데이터는 시간에 따라 계속 변하는 데이터이고, IMF의 새로운 발표마다 기존 수치가 수정될 수도 있다. 따라서 최신 데이터만 저장하는 방식은 사업성 평가나 추세 분석에는 부족하다.

발표 시점 또는 기준 연도를 함께 저장하는 방식으로 누적 저장해야 한다.

현재처럼 if_exists="replace"로 테이블을 매번 갈아엎는 방식이 아니라, 발표 시점 또는 기준 연도를 함께 저장하는 방식으로 누적 저장해야 한다.
예를 들어 테이블 구조를 다음과 같이 확장할 수 있다.
```
Country
Region
GDP_USD_billion
Year
Source
Published_Period
Collected_At
```
각 컬럼의 의미는 다음과 같다.
```
Country: 국가명
Region: 국가가 속한 지역
GDP_USD_billion: billion USD 단위 GDP
Year: GDP 기준 연도
Source: 데이터 출처, 예: IMF WEO
Published_Period: IMF 발표 버전, 예: 2026 April WEO
Collected_At: ETL이 데이터를 수집한 시각
```
이렇게 저장하면 같은 국가라도 연도와 발표 버전에 따라 여러 행을 가질 수 있다. 예를 들어 United States, 2026, April WEO와 United States, 2026, October WEO를 따로 저장할 수 있다. 그러면 최신 데이터 조회뿐 아니라, 과거 발표 데이터와 최신 발표 데이터를 비교하는 것도 가능하다.
ETL 프로세스도 다음과 같이 바뀌어야 한다.
```
Extract:
- IMF API에서 특정 발표 버전 또는 기준 연도의 데이터를 가져온다.

Transform:
- GDP 단위 변환, 국가명 정리, Region 추가를 수행한다.
- Year, Source, Published_Period, Collected_At 컬럼을 추가한다.

Load:
- 기존 테이블을 replace하지 않고 append 방식으로 저장한다.
- 중복 저장을 막기 위해 Country + Year + Published_Period를 기준으로 중복 여부를 확인한다.

Query:
- 최신 데이터만 보고 싶을 때는 가장 최근 Published_Period를 조건으로 조회한다.
- 과거 데이터가 필요할 때는 Year 또는 Published_Period 조건으로 조회한다.결론적으로, 최신 값만 필요하다면 기존 테이블을 갱신하는 방식도 가능하다. 하지만 과거 데이터 조회와 변화 추적이 필요하다면 ETL 결과를 버전별로 누적 저장하는 구조로 바꾸는 것이 더 적절하다.
```

조회 방법 
```
-- 최신 데이터만 조회
SELECT * FROM Countries_by_GDP
WHERE Published_Period = (SELECT MAX(Published_Period) FROM Countries_by_GDP)
ORDER BY GDP_USD_billion DESC;

-- 특정 시점 데이터 조회
SELECT * FROM Countries_by_GDP
WHERE Published_Period = '2026 April WEO'
ORDER BY GDP_USD_billion DESC;

-- 특정 국가의 GDP 변화 추이 조회
SELECT Published_Period, GDP_USD_billion
FROM Countries_by_GDP
WHERE Country = 'United States'
ORDER BY Published_Period;
```

변경 전후 비교
- 현재:  Extract → Transform → Load(replace) → 최신 데이터만 유지
- 변경:  Extract → Transform(날짜 추가) → Load(append) → 과거 데이터 누적
<img width="350" height="200" alt="image" src="https://github.com/user-attachments/assets/38759952-7f21-44b4-ad24-6f70b677e98d" />
