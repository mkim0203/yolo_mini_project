INSERT INTO warehouse_config (
    config_key,
    config_value,
    info
)
VALUES (
    'food_score_threshold',
    '0.4',
    '자동 적재 허용 기준 점수'
);


-- 동 추가.
INSERT INTO public.warehouse(
	warehouse_name, dong, status)
	VALUES ('MAIN 동', 'MAIN', 'active');
INSERT INTO public.warehouse(
	warehouse_name, dong, status)
	VALUES ('동쪽 창고 A', '동쪽 A', 'active');    


-- slot 추가
-- A Line: 12열, 4층
CALL create_warehouse_slots(1, 'A', 12, 4);
-- B Line: 10열, 3층
CALL create_warehouse_slots(1, 'B', 10, 3);
-- C Line: 8열, 2층
CALL create_warehouse_slots(1, 'C', 8, 2);    