CREATE OR REPLACE FUNCTION output_slot(p_release_id BIGINT)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    v_slot_id BIGINT;
    v_storage_id BIGINT;
    v_request_id BIGINT;
BEGIN

    -- 1. release_request 조회
    SELECT slot_id
    INTO v_slot_id
    FROM release_request
    WHERE release_id = p_release_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            '반출 요청 정보를 찾을 수 없습니다. release_id: %',
            p_release_id;
    END IF;


    -- 2. storage_info 조회
    SELECT storage_id, request_id
    INTO v_storage_id, v_request_id
    FROM storage_info
    WHERE slot_id = v_slot_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            '적재 정보를 찾을 수 없습니다. slot_id: %',
            v_slot_id;
    END IF;


    -- 3. warehouse_slot 상태 변경
    UPDATE warehouse_slot
    SET status = 'empty'
    WHERE slot_id = v_slot_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            '창고 슬롯 정보를 찾을 수 없습니다. slot_id: %',
            v_slot_id;
    END IF;


    -- 4. storage_history 정보 업데이트
    UPDATE storage_history
    SET release_request_id = p_release_id,
        output_date = NOW()
    WHERE storage_id = v_storage_id;

    -- IF NOT FOUND THEN
    --     RAISE EXCEPTION
    --         '적재 이력을 찾을 수 없습니다. storage_id: %',
    --         v_storage_id;
    -- END IF;


    -- 5. storage_info 삭제
    DELETE FROM storage_info
    WHERE slot_id = v_slot_id;


    -- 6. release_request 삭제
    DELETE FROM release_request
    WHERE release_id = p_release_id;

	RETURN v_slot_id;
END;
$$;