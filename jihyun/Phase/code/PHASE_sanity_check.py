import os
import re
import glob

import cv2
import argparse
import openpyxl
import itertools
import natsort


parser = argparse.ArgumentParser()
parser.add_argument('--target_dir_path', type=str, default='/Users/jihyunlee/Desktop/data-preprossing/phase', help='path of target directory')
parser.add_argument('--save_path', type=str, default='/Users/jihyunlee/Desktop/data-preprossing/results', help='inspection result save path')
args = parser.parse_args()


def phase_inspection(path_dir):
    # phase.xlsx 파일 리스트
    file_list = glob.glob(os.path.join(path_dir, '*.xlsx'))
    file_list = natsort.natsorted(file_list)

    '''
    error list
        error_no_video : annotation file 에 해당하는 비디오 없음.
        error_no_annotator : column에 annotation 1명인지 확인 (기입되어 있지 않는 경우).
        error_more_annotator : column에 annotation 1명인지 확인 (2명 이상 기입되어 있는 경우).
        error_sequence : column 순서 확인 (armes, only armes 순서).
        error_sheet_no_data : annotation file sheet 에 데이터 존재 여부 확인.
        error_sheet_name : annotation file sheet 명 포맷 확인 (format : ch1_video_01).
        error_other_char : column과 timestamp 이외의 문자 기입 확인.
        error_frame_inconsistency : annotation file 의 timestamp (frame) 이 비디오 frame 보다 많은지 확인.
        error_cannot_read : annotation file encoding 되지 않는 경우, 예외 처리.
    '''

    error_no_video = []
    error_no_annotator = []
    error_more_annotator = []
    error_sequence = []
    error_sheet_no_data = []
    error_sheet_name = []
    error_other_char = []
    error_frame_inconsistency = []
    error_cannot_read = []

    phase_file_cnt = 0
    for phase_file in file_list:
        if phase_file.split('/')[-1][1:4] == 'DS_':
            pass
        elif '~' in phase_file:
            pass

        phase_file_cnt += 1
        print('===> {} target annotation file : {} '.format(phase_file_cnt, phase_file))

        # phase_file = path_dir + '/' + phase_file
        wb = openpyxl.load_workbook(phase_file, data_only=True, read_only=True)
        sheet_names = wb.sheetnames
        sorted_sheet_names = sorted(sheet_names)

        phase_file_without_ext = phase_file.split('/')[-1].split('.')[0]

        try:
            for sheet_name in sorted_sheet_names:
                flag = 1
                
                sheet = wb[sheet_name]
                phase_file_tmp = phase_file_without_ext + '_'+ sheet_name

                '''
                video_dir = os.path.join('/host_server/nas/HUTOM_DATA2/Gastrectomy/YUHS/WJ_Hyung/Videos/Robot/R000{}'.format(phase_file.split('/')[-1][4:7]), 'Videos')
                
                video_list = os.listdir(video_dir)
                video_list.sort()
                
                for video_file in video_list:
                    if video_file[-6:-4] == phase_file_tmp[34:36]:
                        if phase_file_tmp[24:27] in video_file:
                            # video_file = video_file
                            flag = 1
                            break
                '''

                ## error_no_video : annotation file 에 해당하는 비디오 없음.
                ## 일치하는 비디오가 없다면, 다른 것은 검사하지도 않는다. 
                if flag == 0:
                    error_no_video.append(phase_file_tmp)

                else:
                    '''
                    ## error_frame_inconsistency : annotation file 의 timestamp (frame) 이 비디오 frame 보다 많은지 확인.
                    video_file = os.path.join(video_dir, video_file)

                    cap = cv2.VideoCapture(video_file)
                    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

                    body_rows_tmp = itertools.islice(sheet, 1, None)
                    cnt = 0
                    for row in body_rows_tmp:
                        if row[0].value == None:
                            break
                        cnt += 1
                    
                    if cnt < video_length:
                        a = str(phase_file) + ', ' + str(sheet_name) + '__video_frame: ' + str(video_length) + ' __file_frmae: ' + str(cnt)
                        error_frame_inconsistency.append(a)
                    '''

                    body_rows = itertools.islice(sheet, 0, 1)
                    body_rows2 = itertools.islice(sheet, 1, 2)
                    body_rows3 = itertools.islice(sheet, 1, None)

                    total_annotator_list = ['PSR', 'LKM', 'YSH', 'PSH', 'AHMED','ANWAR', 'BERNICE','PARK', 'EDMOND', 'LSH', 'LHJ']
                    
                    ## error_sheet_name : annotation file sheet 명 포맷 확인 (format : ch1_video_01).
                    if sheet_name[0:4] != 'ch1_':
                        h = str(phase_file) + ', ' + str(sheet_name)
                        error_sheet_name.append(h)
                    
                    cnt = 0
                    for row in body_rows:
                        length = len(row)
                        for i in range(1, length):
                            if row[i].value != None:
                                if 'CONSENSUS' in row[i].value.upper():
                                    break
                                cnt += 1
                                length = cnt

                        length += 3

                        ## error_no_annotator : column에 annotation 1명인지 확인 (기입되어 있지 않는 경우).
                        ## error_more_annotator : column에 annotation 1명인지 확인 (2명 이상 기입되어 있는 경우).
                        for m in range(1, length-2):
                            flag = 0
                            for i in range(len(total_annotator_list)):
                                if (isinstance(row[m].value, str) == True):
                                    if total_annotator_list[i] in row[m].value.upper():
                                        flag += 1
                            
                            if flag == 0:
                                a = str(phase_file) + ', ' + str(sheet_name) + '_' + str(m) + '열'
                                error_no_annotator.append(a)
                            
                            if flag > 1:
                                b = str(phase_file) + ', ' + str(sheet_name) + '_' + str(m) + '열'
                                error_more_annotator.append(b)

                        
                        ## error_sequence : column 순서 확인 (armes, only armes 순서).
                        for armes in range(1, length-2, 2):
                            if 'ONLY' in row[armes].value.upper():
                                c = str(phase_file) + ', ' + str(sheet_name) + '_' + str(armes) + '열'
                                error_sequence.append(c)

                        for armes in range(2, length-2, 2):
                            if 'ONLY' not in row[armes].value.upper():
                                f = str(phase_file) + ', ' + str(sheet_name) + '_' + str(armes) + '열'
                                error_sequence.append(f)

                    ## error_sheet_no_data : annotation file sheet 에 데이터 존재 여부 확인.
                    for t in body_rows2:
                        if t[1].value == t[2].value == t[3].value == t[4].value == None:
                            d = str(phase_file) + ', ' + str(sheet_name)
                            error_sheet_no_data.append(d)

                    ## error_other_char : column과 timestamp 이외의 문자 기입 확인.
                    for w in body_rows3:
                        ## 여기서는 무조건 timestamp가 None 값이 나올 때까지만 작동. 
                        ## timestamp None이 잘못되어 있는 경우는 비디오 length와 비교하면서 확인. 
                        if w[0].value == None:
                            break

                        regex = re.compile(r'\d:\d{2}:\d{2}:\d{2}')
                        regex2 = re.compile('\d+')

                        # timestamp 포맷 확인
                        matchobj = regex.fullmatch(w[0].value)
                        if matchobj == None:
                            g = str(phase_file) + ', ' + str(w[0]) + ', ' + str(w[0].value)
                            error_other_char.append(g)

                        # annotation 열 확인
                        for i in range(length-1):
                            matchobj2 = regex2.fullmatch(str(w[i+1].value))

                            if matchobj2 == None:
                                if w[i+1].value != None:
                                    gg = str(phase_file) + ', ' + str(w[i+1])+ ', '+  str(w[i+1].value)
                                    error_other_char.append(gg) 
        
        ## error_cannot_read : annotation file encoding 되지 않는 경우, 예외 처리.
        except:
            error_cannot_read.append(phase_file)



    with open(os.path.join(args.save_path, 'phase_inspection_result.txt'), 'w', encoding='utf-8', newline='' ) as f:

        f.write('Number of Phase files reviewed\n')
        f.write(str(phase_file_cnt))
        f.write('\n\n')
        
        f.write('Error: error_no_video\n')
        for i in range(len(error_no_video)):
            f.write(error_no_video[i])
            f.write("\n")
        
        f.write("\n")
        f.write('Error: error_frame_inconsistency\n')
        for i in range(len(error_frame_inconsistency)):
            f.write(error_frame_inconsistency[i])
            f.write("\n")

        f.write("\n")
        f.write('Error: no_annotator\n')
        for i in range(len(error_no_annotator)):
            f.write(error_no_annotator[i])
            f.write("\n")

        f.write("\n")
        f.write('Error: many_annotator\n')
        for i in range(len(error_more_annotator)):
            f.write(error_more_annotator[i])
            f.write("\n")

        f.write("\n")
        f.write('Error: column_sequence\n')
        for i in range(len(error_sequence)):
            f.write(error_sequence[i])
            f.write("\n")

        f.write("\n")
        f.write('Error: sheet_no_data\n')
        for i in range(len(error_sheet_no_data)):
            f.write(error_sheet_no_data[i])
            f.write("\n")

        f.write("\n")
        f.write('Error: sheet_name\n')
        for i in range(len(error_sheet_name)):
            f.write(error_sheet_name[i])
            f.write("\n")

        f.write("\n")
        f.write('Error: other_char\n')
        for i in range(len(error_other_char)):
            f.write(error_other_char[i])
            f.write("\n")

        f.write("\n")
        f.write('Error: error_cannot_read\n')
        for i in range(len(error_cannot_read)):
            f.write(error_cannot_read[i])
            f.write("\n")


def main():
    target_path = args.target_dir_path
    phase_inspection(target_path)
    
    print("\n\nCOMPLETE!\n\n")


if __name__ == "__main__":
    main()

