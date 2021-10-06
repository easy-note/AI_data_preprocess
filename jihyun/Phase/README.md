# ai-data-preprocess
## Phase, CAM, NIR
- 데이터 값 확인
    - Phase
        - error_no_video : annotation file 에 해당하는 비디오 없음.
        - error_no_annotator : column에 annotation 1명인지 확인 (기입되어 있지 않는 경우).
        - error_more_annotator : column에 annotation 1명인지 확인 (2명 이상 기입되어 있는 경우).
        - error_sequence : column 순서 확인 (armes, only armes 순서).
        - error_sheet_no_data : annotation file sheet 에 데이터 존재 여부 확인.
        - error_sheet_name : annotation file sheet 명 포맷 확인 (format : ch1_video_01).
        - error_other_char : column과 timestamp 이외의 문자 기입 확인.
        - error_frame_inconsistency : annotation file 의 timestamp (frame) 이 비디오 frame 보다 많은지 확인.
        - error_cannot_read : annotation file encoding 되지 않는 경우, 예외 처리.

    - CAM, NIR
        - error_no_video : annotation file 에 해당하는 비디오 없음.
        - error_file_name : annotation file 명 포맷 확인 (format : R001_CAMIO_ch1_video_03_1.csv).
        - error_column_name : annotation file dml column 확인 ('start', 'end').
        - error_time_overlap : annotation file 의 timestamp 중복 확인.
        - error_other_char : column과 timestamp 이외의 문자 기입 확인.
        - error_cannot_read : annotation file encoding 되지 않는 경우, 예외 처리.

