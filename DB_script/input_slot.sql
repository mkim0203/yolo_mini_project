CREATE OR REPLACE FUNCTION public.input_slot(p_request_id bigint)
    RETURNS bigint
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    v_info VARCHAR(100);
	v_expiry_date TIMESTAMP;
	v_image_type VARCHAR(50);
	v_image_data BYTEA;
	v_warehouse_id BIGINT;
	v_slot_id BIGINT;
	v_storage_id BIGINT;
BEGIN
	-- 적제 요청 ID기준으로 slot에 사용 전환 및 적재 정보 등록

	--1. request_id로 적재 요청 조회
	select info, expiry_date, image_type, image_data 
	into v_info, v_expiry_date, v_image_type, v_image_data 
	from storage_request
	where request_id = p_request_id;

	IF NOT FOUND THEN
	    RAISE EXCEPTION '적재 요청 정보를 찾을 수 없습니다. request_id: %', p_request_id;
	END IF;

	--2. 비어 있는 슬롯(empty) 검색
	SELECT warehouse_id, slot_id
	INTO v_warehouse_id, v_slot_id
	FROM warehouse_slot
	WHERE status = 'empty'
	ORDER BY warehouse_id, line_code, floor, column_no
	LIMIT 1
	FOR UPDATE SKIP LOCKED;
	
	IF NOT FOUND THEN
	    RAISE EXCEPTION '사용 가능한 빈 슬롯이 없습니다.';
	END IF;
	
	--3. 선택한 슬롯 상태를 used로 변경
	UPDATE warehouse_slot
	SET status = 'used'
	WHERE slot_id = v_slot_id;
	
	--4. storage_info 테이블에 적재 정보 INSERT
	INSERT INTO storage_info(slot_id, request_id, info, image_type, image_data, expiry_date)
	VALUES(v_slot_id, p_request_id, v_info, v_image_type, v_image_data, v_expiry_date)
	RETURNING storage_id INTO v_storage_id;
	-- insert 이후 storage_id 가져와야함.
	
	--5. history 테이블에 작업 이력 INSERT
    INSERT INTO public.storage_history(
	warehouse_id, slot_id, storage_id, info, expiry_date, storage_request_id, input_date)
	VALUES (v_warehouse_id, v_slot_id, v_storage_id, v_info, v_expiry_date, p_request_id, NOW());

	--6. storage_request 테이블에서 제거
	DELETE FROM storage_request
	WHERE request_id = p_request_id;
	
    RETURN v_slot_id;
END;
$BODY$;