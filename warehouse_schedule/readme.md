# 스케줄링 처리


* 적재요청이 들어온 내용 조회하여 분류 작업 api에 요청
    1. warehouse api 적재요청 항목 조회
    2. warehouse ai 에 분류 요청
    3. 요청결과 warehouse api에 update 진행

* 유통기한 만료 임박 물건 반출
    1. 자동 반출 기준 조회 : warehouse api
    2. warehouse api에서 반출 대상 조회
    3. warehouse api에 반출 등록

