# ai-data-preprocess
## Bleeding Grading
- 완료된 individual 받아서 consensus 제공
    - 2개의 individual 파일을 병합한 뒤, 레이블 값이 일치되지 않은 열을 표시해서 consensus 파일로 제공

- 파일 종류 별
    - channel (sanity check, consensus)
    - patient (sanity check, consensus)

- sanity check list
    - error_column : column 명 [location (x,y), Timestamp, Site, ..] 확인
    - error_channel : 파일 간 channel 일치 여부 확인
    - error_row_count : 파일 간 row count 일치 여부 확인
    - error_except : exception
