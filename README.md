# MBTIgram Fask server
## 개요
메인 서버인 스프링 서버에서의 요청에 따라 작성글을 바탕으로 MBTI분석 후 결과를 스프링 서버에 반환한다.

Front End: <https://github.com/SPP-Zizon-Ulzzang/Zizon-Ulzzang-FE>

스프링 서버: <https://github.com/SPP-Zizon-Ulzzang/Zizon-Ulzzang-BE>
## 기능
### 1. 인스타그램 게시글 분석
1. 사용자의 인스타그램 ID를 메인서버로 부터 전달받는다.
2. Instagrapi(<https://github.com/adw0rd/instagrapi>)를 통해 최근 게시글의 텍스트를 조회한다.
3. 모델을 통해 추출된 텍스트를 바탕으로 사용자의 MBTI를 예측한다.
4. 결과를 메인서버에 반환한다.
### 2. 자기소개 분석
1. 사용자가 작성한 자기소개 글을 메인서버로 부터 전달받는다.
2. 모델을 통해 해당 자기소개 글을 바탕으로 사용자의 MBTI를 예측한다.
3. 결과를 메인서버에 반환한다.

## 예측 모델
### 1. 학습 데이터
(MBTI) Myers-Briggs Personality Type Dataset
[Link] https://www.kaggle.com/datasets/datasnaek/mbti-type
mbti_1.csv

MBTI Personality Types 500 Dataset
[Link] https://www.kaggle.com/datasets/zeyadkhalid/mbti-personality-types-500-dataset
MBTI 500.csv
해당 데이터 셋은 Reddit에서 수집되었으며 작성글에 대해 작성자의 MBTI가 라벨링되어있다.
### 2. 전처리 과정
2-1. 클래스 불균형 해소

- SMOTE를 이용하여 MBTI의 각 유형별 샘플 개수의 불균형의 해소

2-2. 불용어 처리

- 유의미한 토큰만을 위한 불용어 처리
- 링크 제거, 축약형 변환, 특수기호 제거, 대소문자 변환 등

2-3. TF-IDF 벡터화

- 단어별 중요도에 따른 분류를 위한 TF-IDF벡터화

### 3. 모델링
GridSearchCV를 이용하여 최적의 하이퍼 파라미터로 튜닝
SVM기반 Linear SVC모델 사용

### 4. 모델 성능 평가
Accuracy와 F1-score 등 다양한 지표 사용
