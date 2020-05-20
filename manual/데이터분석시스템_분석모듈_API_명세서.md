## **데이터 분석 시스템 분석모듈 API 명세서**


1.  **API 목록**

    1-1.  **API URI 맵**             

- 메인 URL 패턴 :  /analyticsModule
    - 머신러닝 관리: /analyticsModule/ml
    - 딥러닝 관리 : /analyticsModule/dl

|**순번**| **메인 URL** | **기능구분**  | **HTTP Method** | **URI**                                              | **Header**           | **설명**                      |
|----|---------------------|--------------|-------------|--------------------------------------------------|------------------|---------------------------|
| 1  | /analyticsModule    | 헬스체크             | GET         | /healthCheck                                     | application/json | 헬스체크                      |
| 2  | /analyticsModule    | 알고리즘조회          | GET         | /algorithm                                       | application/json | 분석 가능한 알고리즘 리스트 조회    |
| 3  | /analyticsModule    |                    | GET         | /algorithm/{id}                                  | application/json | 분석 가능한 알고리즘 개별 조회     |
| 4  | /analyticsModule    | 전처리기능조회         | GET         | /preprocessFunction                              | application/json | 사용 가능한 전처리 기능 리스트 조회      |
| 5  | /analyticsModule    |                    | GET         | /preprocessFunction/{id}                         | application/json | 사용 가능한 전처리 기능 개별 조회       |
| 6  | /analyticsModule    | 로컬파일 조회         | GET         | /localFiles?commend=get_list&path=               | application/json | 특정 디렉토리의 로컬 파일 리스트 조회     |
| 7  | /analyticsModule    | 파일샘플 조회         | GET         | /localFiles?commend=get_sample&path=             | application/json | 특정 디렉토리의 로컬 파일 샘플 조회      |
| 8  | /analyticsModule/ml | 원본데이터 관리        | GET         | /originalData                                    | application/json | 원본 데이터 리스트 조회             |
| 9  | /analyticsModule/ml |                    | POST        | /originalData                                    | application/json | 원본 데이터 생성                 |
| 10 | /analyticsModule/ml |                    | GET         | /originalData/{id}                               | application/json | 원본 데이터 개별 조회              |
| 11 | /analyticsModule/ml |                    | PATCH       | /originalData/{id}                               | application/json | 원본 데이터 전처리 테스트            |
| 12 | /analyticsModule/ml |                    | DELETE      | /originalData/{id}/download                      | application/json | 원본 데이터 삭제                 |
| 13 | /analyticsModule/ml |                    | GET         | /originalData/{id}/download                      | octet-stream     | 원본 데이터 다운로드               |
| 14 | /analyticsModule/ml | 전처리데이터 관리      | GET         | /preprocessedData                                | application/json | 전처리 데이터 리스트 조회            |
| 15 | /analyticsModule/ml |                    | POST        | /preprocessedData                                | application/json | 전처리 데이터 생성                |
| 16 | /analyticsModule/ml |                    | GET         | /preprocessedData{id}                            | application/json | 전처리 데이터 개별 조회             |
| 17 | /analyticsModule/ml |                    | DELETE      | /preprocessedData/{id}                           | application/json | 전처리 데이터 삭제                |
| 18 | /analyticsModule/ml |                    | GET         | /preprocessedData/{id}/download?type=data        | octet-stream     | 저장된 전처리 데이터 다운로드          |
| 19 | /analyticsModule/ml |                    | GET         | /preprocessedData/{id}/download?type=transformer | octet-stream     | 저장된 전처리기 다운로드             |
| 20 | /analyticsModule/ml | 모델 관리            | GET         | /model                                           | application/json | 학습된 모델 리스트 조회             |
| 21 | /analyticsModule/ml |                    | POST        | /model                                           | application/json | 모델 생성                     |
| 22 | /analyticsModule/ml |                    | GET         | /model/{id}                                      | application/json | 학습된 모델 개별 조회              |
| 23 | /analyticsModule/ml |                    | PATCH       | /model/{id}                                      | application/json | 모델 학습 중지, 재요청 및 적용(테스트)   |
| 24 | /analyticsModule/ml |                    | DELETE      | /model/{id}                                      | application/json | 학습된 모델 삭제                 |
| 25 | /analyticsModule/ml |                    | GET         | /model/{id}/download                             | octet-stream     | 학습된 모델 다운로드               |
| 26 | /analyticsModule/dl | (이미지) 데이터 관리   | GET         | /originalData                                    | application/json | 이미지 데이터 리스트 조회            |
| 27 | /analyticsModule/dl |                    | POST        | /originalData                                    | application/json | 이미지 데이터 생성 [폴더로 구분되는 경로]  |
| 28 | /analyticsModule/dl |                    | GET         | /originalData/{id}                               | application/json | 이미지 데이터 개별 조회 [이미지 정보 조회] |
| 29 | /analyticsModule/dl |                    | DELETE      | /originalData/{id}                               | application/json | 이미지 데이터 삭제                |
| 30 | /analyticsModule/dl | (이미지) 모델 관리     | GET         | /model                                           | application/json | 모델 리스트 조회                 |
| 31 | /analyticsModule/dl |                    | POST        | /model                                           | application/json | 모델 생성 [전이학습을 위한 옵션 전달]    |
| 32 | /analyticsModule/dl |                    | GET         | /model/{id}                                      | application/json | 모델 개별 조회 [학습 비동기 처리 업데이트] |
| 33 | /analyticsModule/dl |                    | DELETE      | /model/{id}                                      | application/json | 모델 삭제                     |
| 34 | /analyticsModule/dl |                    | GET         | /model/{id}/download?type=                       | octet-stream     | 모델 다운로드 [네트워크&가중치]        |
2.  **API 명세**

> [데이터 분석 시스템 분석모듈 API 세부 명세](https://documenter.getpostman.com/view/9242058/SzKWtcRF?version=latest)
