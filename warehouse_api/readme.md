### api 기능 작업
### 데이터 조회 및 저장

# 조회
	현황
		창고 동 상태
			GET /warehouses 
		창고 동기준 line 상태/ line 전체
			GET /warehouse/{warehouse_id}/lines
			GET /warehouse/{warehouse_id}/line/{line_code}
	적제 요청 목록
		GET /storages
	적제 반출 이력
		GET /releases
	만료 대상 조회
		GET /expiry
	대시보드
		전체 적재율, 빈 공간 및 점검 현황, 식품 분류 결과, 유통기한 임박 현황
# 저장
	적제 요청
		POST /storage
	반출 요청
		POST /releases/{slot_id}
	slot 상태 변경
		PUT /slots/{slot_id}
	상품 slot 이동
		PUT /slots/{slot_id}/move/{move_slot_id}


## 환경 파일 생성후 진행 .env
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=ragdb
DB_USER=
DB_PW=