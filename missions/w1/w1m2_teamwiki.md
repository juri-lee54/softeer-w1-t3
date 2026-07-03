## 1주차 미션2 3팀 위키
### 각자가 이해하기 어려웠던, 또는 이해하지 못한 keyword에 대해서 함께 토의해 봅시다.
#### @jiyoon-ryu
- TOP
  - TOP은 조회 결과 중 일부 행만 가져오는 문법이다.
  - 처음에는 SQLite에서도 사용할 수 있는 줄 알았지만, TOP은 SQL Server 문법이고 SQLite에서는 지원하지 않는다.
  - 따라서 SQLite에서는 LIMIT을 사용해 같은 기능을 구현해야 했다.
- ALL
  - ALL은 서브쿼리의 모든 결과와 비교할 때 사용하는 문법이다.
  - 처음에는 정확히 어떤 상황에서 쓰는지 이해하기 어려웠다.
  - SQLite에서는 ALL을 지원하지 않아 MAX()나 MIN()을 사용해 비슷하게 대체할 수 있었다.
- ANY
  - ANY는 서브쿼리 결과 중 하나라도 조건을 만족하면 참이 되는 문법이다.
  - ALL은 모든 값이 조건을 만족해야 하고, ANY는 하나만 만족해도 된다는 차이가 있다.
  - SQLite에서는 ANY를 그대로 사용할 수 없어 IN이나 EXISTS로 대체할 수 있었다.
- %와 _
  - %와 _는 LIKE에서 사용하는 와일드카드이다.
  - 둘 다 아무 문자를 의미해서 헷갈렸지만, %는 글자 수와 상관없는 여러 글자를 의미하고 _는 정확히 한 글자만 의미한다.예를 들어 A%는 A로 시작하는 모든 문자열을 찾고, _r%는 두 번째 글자가 r인 문자열을 찾는다.

#### @taeju-moon
- select * into DES from SOURCE 구문: 어떤 테이블이 소스고 어떤 테이블이 목적지인지 헷갈렸다. source로부터 특정 컬럼들을 des라는 테이블로써 복제하는 기능이다. 특히 sqlite에서는 지원하지 않아 CREATE TABLE ... AS SELECT ... 구문을 사용하여 우회하여야 했다.
- union과 union all의 차이점: 두 키워드의 차이점을 이해하기 어려웠다. union은 중복을 허용하지 않고, union all은 허용한다고 한다. 그러므로 연산 성능은 union all이 빨라 실제 실무에서는 union all을 많이 사용한다고 한다.
- procedure: 프로시저의 개념에 대해서 이해가 어려웠다. sqlite에서도 없는 개념이다. 함수와 같은 개념이라서, 파이썬 함수로써 코드 블럭을 실행해보는 것으로 실습을 대체했다.
- where vs having: 두 구문의 차이점이 이해가 어려웠다. where은 연산의 select시점에서 실행되는데, having은 이미 group by로 묶은 후에 실행된다.

#### @lsy341
- NULL은 = 로 비교가 안 된다. IS NULL 을 써야 한다.
  - ❌ WHERE PostalCode = NULL
  - ✅ WHERE PostalCode IS NULLWHERE PostalCode IS NOT NULLNULL이 "알 수 없는 값"이라서 = NULL 이 항상 false로 처리되기 때문이다.
- LIKE = 문자열 패턴 매칭 조건
  - 완전히 일치하는 게 아니라 부분적으로 일치하는 걸 찾을 때 쓴다.
  - 와일드카드 2가지:
```
기호 의미 예시     % 0개 이상의 아무 문자 'A%' → A로 시작하는 모든 것   _ 정확히 1개의 아무 문자 '_n%' → 두번째 글자가 n인 것   WHERE CustomerName LIKE 'A%'     -- A로 시작
WHERE CustomerName LIKE '%a'     -- a로 끝
WHERE CustomerName LIKE '%or%'   -- or 포함
WHERE CustomerName LIKE '_n%'    -- 두번째 글자가 n
```
- 검색창에서 키워드 검색하는 것과 같다. %가 * 역할이다.
- AND와 OR이 괄호 없이 있으면 AND가 먼저 실행된다.

#### @juri-lee54
- TOP : MySQL/표준 SQL의 LIMIT과 같은 역할인데 SQL Server 전용 문법이라 SQLite에서는 아예 안 먹힘. DB마다 "상위 N개 가져오기" 문법이 다르다는 걸 처음 인지함.
- = ALL (...) : 비교 연산자에 ALL/ANY/SOME을 붙이는 문법 자체가 생소했음. 서브쿼리 결과 전부와 비교한다는 의미인데, SQLite는 이 수식어 자체를 지원 안 함.
- CREATE PROCEDURE — SQLite는 프로시저 개념이 없어서 함수/뷰로 대체해야 한다는 것도 헷갈렸음.
