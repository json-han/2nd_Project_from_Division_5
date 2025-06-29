### **소스코드 명세서: 네이버 금융 종목토론실 크롤러**

#### **1. 개요 (Overview)**

본 문서는 네이버 금융(Naver Finance)의 인기 검색 종목 토론실 게시글을 수집하는 Python 스크립트에 대한 명세서입니다. 스크립트는 두 단계의 크롤링 프로세스를 통해 동작합니다. 첫 번째 단계에서는 각 종목의 게시글 목록(제목, 작성자, 날짜, 조회수 등)을 수집하여 CSV 파일로 저장하고, 두 번째 단계에서는 저장된 목록을 바탕으로 각 게시글의 상세 내용과 댓글을 수집하여 최종 데이터를 생성합니다.

- **프로젝트명**: 네이버 금융 종목토론실 크롤러
- **소스파일명**:
  - `naver_stock_community_crwaler.ipynb`
- **최종 산출물**:
  - `data/naver_stock_community_{timestamp}.csv`: 게시글 상세 내용 및 댓글이 병합된 최종 데이터

#### **2. 주요 기능 (Key Features)**

- **인기 종목 코드 수집**: 네이버 금융의 '인기 검색 종목' 페이지에서 상위 종목들의 코드를 자동으로 추출합니다.
- **게시글 목록 크롤링**: 각 종목에 대해 지정된 페이지 수만큼 게시글 목록(날짜, 제목, 닉네임, 조회수, 공감/비공감 수)을 수집합니다.
- **동적 페이지 처리**: Selenium을 사용하여 JavaScript로 동적으로 로드되는 콘텐츠를 처리합니다.
- **게시글 상세 내용 및 댓글 수집**: 수집된 게시글 목록을 기반으로 각 게시글의 본문 내용과 모든 댓글을 수집합니다.
- **데이터 저장**: 수집된 데이터를 두 단계에 걸쳐 Pandas DataFrame으로 관리하고, 최종 결과를 UTF-8 인코딩의 CSV 파일로 저장합니다.
- **안정성 및 예외 처리**: `WebDriverWait`을 통한 명시적 대기, `try-except` 구문을 활용한 타임아웃 및 요소 부재 예외를 처리하여 크롤링 중단 위험을 최소화합니다.
- **진행 상황 시각화**: `tqdm` 라이브러리를 사용하여 크롤링 진행 상황을 프로그레스 바로 표시합니다.

#### **3. 시스템 요구사항 (System Requirements)**

- **언어**: Python 3.8 이상
- **필수 라이브러리**:
  - `pandas`: 데이터 구조화 및 분석
  - `selenium`: 웹 브라우저 자동화 및 동적 크롤링
  - `beautifulsoup4`: HTML/XML 파싱
  - `requests`: HTTP 요청 (get_item_code_list 함수에서 사용)
  - `tqdm`: 콘솔 진행률 표시
- **웹 브라우저**: Google Chrome

#### **4. 실행 방법 (How to Run)**

1. **라이브러리 설치**:
   ```bash
   pip install pandas selenium beautifulsoup4 requests tqdm
   ```
2. **스크립트 실행**:
   - jupyter 환경에서 코드 한블럭씩 실행합니다.
3. **결과 확인**:
   - 스크립트 실행이 완료되면 `data` 폴더 내에 `articleList_...` 와 `naver_stock_community_...` CSV 파일이 생성됩니다.

#### **5. 소스코드 구조 (Source Code Structure)**

- **전역 변수 및 상수**: 크롤링에 필요한 기본 설정값(헤더, 파일 경로, 기본 페이지 수 등)을 정의합니다.
- **함수 (Functions)**: 각 기능 단위로 모듈화된 함수들로 구성됩니다.
- **메인 실행 블록 (`if __name__ == "__main__":`)**: 전체 크롤링 프로세스를 순차적으로 조율하고 실행합니다.

#### **6. 함수별 명세 (Function-by-Function Specification)**


| 함수명                | `initialize_driver()`                                                                                                            |
| :---------------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| **설명**              | Selenium WebDriver를 초기화하고 필요한 옵션을 설정하여 반환합니다. Headless 모드로 동작하여 실제 브라우저 창을 띄우지 않습니다.  |
| **인자 (Parameters)** | 없음                                                                                                                             |
| **반환값 (Return)**   | `webdriver.Chrome`: 설정이 완료된 Chrome WebDriver 인스턴스                                                                      |
| **주요 로직**         | - Headless, no-sandbox 등 안정적인 실행을 위한 Chrome 옵션 설정<br>- 사용자 에이전트 및 언어 설정<br>- 페이지 로드 타임아웃 설정 |


| 함수명                | `get_item_code_list()`                                                                                                            |
| :---------------------- | :---------------------------------------------------------------------------------------------------------------------------------- |
| **설명**              | 네이버 금융의 '인기 검색 종목' 페이지에 접속하여 상위 종목들의 코드를 리스트 형태로 추출합니다.                                   |
| **인자 (Parameters)** | 없음                                                                                                                              |
| **반환값 (Return)**   | `list`: 종목 코드 문자열을 담고 있는 리스트 (예: `['005930', '035720']`)                                                          |
| **주요 로직**         | -`requests`와 `BeautifulSoup`를 사용하여 정적 페이지 파싱<br>- 정규표현식을 사용하여 `href` 속성에서 종목 코드(6자리 숫자)만 추출 |


| 함수명                | `get_item_url(item_code, page_no=1)`                                             |
| :---------------------- | :--------------------------------------------------------------------------------- |
| **설명**              | 주어진 종목 코드와 페이지 번호를 조합하여 네이버 금융 토론실의 URL을 생성합니다. |
| **인자 (Parameters)** | `item_code` (str): 종목 코드<br>`page_no` (int): 페이지 번호 (기본값: 1)         |
| **반환값 (Return)**   | `str`: 완성된 URL 문자열                                                         |


| 함수명                | `get_last_page(driver, item_code)`                                                                                                                                                              |
| :---------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **설명**              | 특정 종목 토론실의 마지막 페이지 번호를 동적으로 가져옵니다.                                                                                                                                    |
| **인자 (Parameters)** | `driver` (WebDriver): Selenium WebDriver 인스턴스<br>`item_code` (str): 종목 코드                                                                                                               |
| **반환값 (Return)**   | `int`: 마지막 페이지 번호. 실패 시 기본값(`last_page_default`) 반환.                                                                                                                            |
| **주요 로직**         | - '맨뒤' 페이지로 가는 링크(`td.pgRR a`)를 `WebDriverWait`으로 탐색<br>- 링크의 `href` 속성에서 정규표현식으로 페이지 번호를 추출<br>- 타임아웃 등 예외 발생 시 경고 메시지 출력 후 기본값 반환 |


| 함수명                | `get_one_page(driver, item_code, page_no)`                                                                                                                                                                                                                                                                                        |
| :---------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **설명**              | 특정 종목의 단일 페이지에 있는 모든 게시글의 메타데이터를 수집합니다.                                                                                                                                                                                                                                                             |
| **인자 (Parameters)** | `driver` (WebDriver): Selenium WebDriver 인스턴스<br>`item_code` (str): 종목 코드<br>`page_no` (int): 수집할 페이지 번호                                                                                                                                                                                                          |
| **반환값 (Return)**   | `pd.DataFrame`: 해당 페이지의 게시글 목록 정보를 담은 데이터프레임                                                                                                                                                                                                                                                                |
| **주요 로직**         | -`driver.get()`으로 페이지 이동 후 `WebDriverWait`으로 게시글 목록이 로드될 때까지 대기<br>- `BeautifulSoup`으로 현재 페이지 소스를 파싱<br>- `<tr>` 태그를 순회하며 유효한 게시글 행 필터링 (날짜 형식 확인)<br>- 제목, 댓글 수, 게시글 번호(nid), 닉네임, 조회수, 공감/비공감 수 추출<br>- '클린봇'에 의해 숨겨진 게시글은 제외 |


| 함수명                | `get_all_pages(driver, item_code)`                                                                                                                                                                                               |
| :---------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **설명**              | 특정 종목에 대해`get_last_page`로 마지막 페이지를 확인하고, 1페이지부터 마지막 페이지까지 모든 게시글 목록을 수집하여 하나의 데이터프레임으로 합칩니다.                                                                          |
| **인자 (Parameters)** | `driver` (WebDriver): Selenium WebDriver 인스턴스<br>`item_code` (str): 종목 코드                                                                                                                                                |
| **반환값 (Return)**   | `pd.DataFrame`: 해당 종목의 모든 게시글 목록 정보를 담은 데이터프레임                                                                                                                                                            |
| **주요 로직**         | -`get_last_page()` 호출하여 전체 페이지 수 확인<br>- `for` 루프를 통해 각 페이지에 대해 `get_one_page()` 호출<br>- 반환된 데이터프레임들을 리스트에 저장 후 `pd.concat`으로 병합<br>- 숫자형 컬럼들의 데이터 타입을 `int`로 변환 |


| 함수명                | `get_article_content(article_list)`                                                                                                                                                                                                                                                                                                   |
| :---------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **설명**              | 게시글 목록(`[종목코드, 게시글 ID]`)을 받아 각 게시글의 상세 페이지에 접속하여 본문 내용과 댓글을 수집합니다.                                                                                                                                                                                                                         |
| **인자 (Parameters)** | `article_list` (list): `[종목코드, 게시글 ID]` 형태의 리스트들의 리스트                                                                                                                                                                                                                                                               |
| **반환값 (Return)**   | `pd.DataFrame`: 게시글 ID, 본문 내용, 댓글을 담은 데이터프레임                                                                                                                                                                                                                                                                        |
| **주요 로직**         | - 함수 내에서 독립적인 WebDriver를 새로 초기화하고 종료함<br>- `tqdm`을 사용하여 진행 상황 표시<br>- `article_list`를 순회하며 각 게시글의 상세 URL 생성 및 접속<br>- `div#body`에서 게시글 본문, `span.u_cbox_contents`에서 댓글 추출<br>- 예외 발생 시 빈 값으로 처리하고 다음 게시글로 진행<br>- 수집된 내용을 데이터프레임에 추가 |

#### **7. 전역 변수 및 상수 (Global Variables and Constants)**

- `headers`: HTTP 요청 시 사용할 User-Agent 헤더
- `current_date`: 파일명에 사용될 현재 시각 타임스탬프
- `filepath`: 게시글 목록이 저장될 CSV 파일 경로
- `last_page_default`: 마지막 페이지 번호를 가져오지 못했을 때 사용할 기본 페이지 수 (기본값: 5)

#### **8. 실행 로직 (`if __name__ == "__main__":`)**

1. **초기화**: 메인 WebDriver 인스턴스를 생성합니다.
2. **1단계: 게시글 목록 수집**
   - `get_item_code_list()`를 호출하여 크롤링할 종목 코드 목록을 가져옵니다.
   - 각 종목 코드에 대해 `get_all_pages()`를 실행하여 게시글 목록을 수집하고, 결과를 `df_list`에 추가합니다.
   - 수집된 모든 데이터프레임을 `pd.concat`으로 병합하여 `df_all`을 생성합니다.
   - `df_all`을 `articleList_{timestamp}.csv` 파일로 저장합니다.
3. **에러 처리**: `finally` 블록을 통해 어떤 상황에서든 메인 WebDriver가 `driver.quit()`으로 종료되도록 보장합니다.
4. **2단계: 게시글 내용 및 댓글 수집**
   - 저장된 `articleList_{timestamp}.csv` 파일을 다시 로드합니다.
   - `get_article_content` 함수에 전달할 `[종목코드, 게시글 ID]` 리스트를 생성합니다.
   - `get_article_content()`를 호출하여 상세 내용(`df_article`)을 가져옵니다.
5. **데이터 병합 및 최종 저장**
   - 원본 목록 데이터프레임(`df_all`)과 상세 내용 데이터프레임(`df_article`)을 '게시글' ID 기준으로 병합합니다.
   - 최종 병합된 데이터를 `naver_stock_community_{timestamp}.csv` 파일로 저장합니다.

#### **9. 개선 및 유의사항 (Improvements and Notes)**

- **효율성**: 현재 구조는 목록 수집과 내용 수집이 완전히 분리되어 있습니다. 만약 실시간성이 중요하다면, `get_one_page` 함수 내에서 게시글 링크를 발견하는 즉시 새 탭으로 열어 내용을 수집하는 비동기 방식 또는 멀티스레딩/프로세싱을 도입하여 속도를 향상시킬 수 있습니다.
- **IP 차단 위험**: 네이버 서버에 단시간에 너무 많은 요청을 보내면 IP가 일시적으로 차단될 수 있습니다. `time.sleep()`을 통해 요청 간 간격을 조절하고 있으나, 대규모 크롤링 시에는 프록시(Proxy) 서버를 활용하는 것이 더 안정적입니다.
- **웹사이트 구조 변경**: 네이버 금융 페이지의 HTML 구조가 변경되면 CSS 선택자가 동작하지 않아 크롤러가 실패할 수 있습니다. 주기적인 유지보수가 필요합니다.
