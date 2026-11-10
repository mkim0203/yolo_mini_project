CREATE OR REPLACE PROCEDURE public.create_warehouse_slots(
	IN p_warehouse_id bigint,
	IN p_line_code character varying,
	IN p_column_count integer,
	IN p_floor_count integer)
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
	-- A Line: 12열, 4층
	-- CALL create_warehouse_slots(1, 'A', 12, 4);
	-- B Line: 10열, 3층
	-- CALL create_warehouse_slots(1, 'B', 10, 3);
	-- C Line: 8열, 2층
	-- CALL create_warehouse_slots(1, 'C', 8, 2);

    -- 입력값 검증
    IF p_warehouse_id IS NULL
       OR p_line_code IS NULL
       OR TRIM(p_line_code) = ''
       OR p_column_count IS NULL
       OR p_column_count <= 0
       OR p_floor_count IS NULL
       OR p_floor_count <= 0 THEN

        RAISE EXCEPTION '입력값이 올바르지 않습니다.';
    END IF;

    -- 슬롯 자동 생성
    INSERT INTO warehouse_slot (
        warehouse_id,
        line_code,
        column_no,
        floor,
		status
    )
    SELECT
        p_warehouse_id,
        p_line_code,
        c,
        f,
		'empty'
    FROM generate_series(1, p_column_count) AS c
    CROSS JOIN generate_series(1, p_floor_count) AS f
    ON CONFLICT (warehouse_id, line_code, column_no, floor)
    DO NOTHING;

END;
$BODY$;