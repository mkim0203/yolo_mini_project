CREATE OR REPLACE PROCEDURE create_warehouse_slots(
    p_warehouse_id BIGINT,
    p_line_count INTEGER,
    p_column_count INTEGER,
    p_floor_count INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- warehouse_id: 창고 ID
    -- line_count: 행 개수 (10개)
    -- column_count: 열 개수 (12칸)
    -- floor_count: 층수 (4층)
    -- 슬롯 자동 생성 프로시저 CALL create_warehouse_slots(1, 10, 12, 4);

    -- 입력값 검증
    IF p_line_count <= 0
       OR p_column_count <= 0
       OR p_floor_count <= 0 THEN
        RAISE EXCEPTION '생성 개수는 모두 1 이상이어야 합니다.';
    END IF;

    -- 적재 위치 자동 생성
    INSERT INTO warehouse_slot (
        warehouse_id,
        line_code,
        column_no,
        floor,
        status
    )
    SELECT
        p_warehouse_id,
        CHR(64 + r),
        c,
        f,
        'active'
    FROM generate_series(1, p_line_count) AS r
    CROSS JOIN generate_series(1, p_column_count) AS c
    CROSS JOIN generate_series(1, p_floor_count) AS f
    ON CONFLICT (warehouse_id, line_code, column_no, floor)
    DO NOTHING;

END;
$$;
