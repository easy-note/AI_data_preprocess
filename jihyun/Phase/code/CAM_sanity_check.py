import os
import re
import csv
import glob
import pandas as pd

import argparse 
import natsort

parser = argparse.ArgumentParser()
parser.add_argument('--target_dir_path', type=str, default='/Users/jihyunlee/Desktop/data-preprossing/cam', help='path of target directory')
parser.add_argument('--save_path', type=str, default='/Users/jihyunlee/Desktop/data-preprossing/results', help='inspection result save path')
args = parser.parse_args()


def time_to_idx(time):
    fps = 30
    t_segment = time.split(':')
    idx = int(t_segment[0])*3600 + int(t_segment[1])*60 + int(t_segment[2])
    frame = idx * fps + int(t_segment[3])

    return frame


def cam_inspection(path_dir):
    # cam.csv 파일 리스트
    file_list = glob.glob(os.path.join(path_dir, '*.csv'))
    file_list = natsort.natsorted(file_list)

    '''
    error list
        error_no_video : annotation file 에 해당하는 비디오 없음.
        error_file_name : annotation file 명 포맷 확인 (format : R001_CAMIO_ch1_video_03_1.csv).
        error_column_name : annotation file dml column 확인 ('start', 'end').
        error_time_overlap : annotation file 의 timestamp 중복 확인.
        error_other_char : column과 timestamp 이외의 문자 기입 확인.
        error_cannot_read : annotation file encoding 되지 않는 경우, 예외 처리.
    '''

    error_no_video = []
    error_file_name = []
    error_column_name = []
    error_time_overlap = []
    error_other_char = []
    error_cannot_read = []
    

    cam_file_cnt = 0
    for cam_file in file_list:
        
        flag = 1
        
        if cam_file.split('/')[-1][0:1] == 'R':
            cam_file_cnt += 1
            print('===> {} target annotation file : {} '.format(cam_file_cnt, cam_file))

            '''
            video_dir = os.path.join('/host_server/nas/HUTOM_DATA2/Gastrectomy/YUHS/WJ_Hyung/Videos/Robot/R000', cam_file.split('/')[-1][1:4], 'Videos')

            video_list = os.listdir(video_dir)
            video_list.sort()

            for video_file in video_list:
                if video_file[-6:-4] == cam_file.split('/')[-1][21:23]: # video no 일치 여부 확인 (03 == 03)
                    if cam_file[11:14] in video_file: # channel 확인 (ch1)
                        # video_file = video_file
                        flag = 1
                        break
            '''

            ## error_no_video : annotation file 에 해당하는 비디오 없음.
            ## 일치하는 비디오가 없다면, 다른 것은 검사하지도 않는다. 
            if flag == 0:
                error_no_video.append(cam_file)
            
            else:
                ## error_file_name : annotation file 명 포맷 확인 (format : R001_CAMIO_ch1_video_03_1.csv). 
                if ('ch2' in cam_file) or (' ' in cam_file):
                    error_file_name.append(cam_file)

                regex = re.compile(r'R\d{3}_CAMIO_ch\d{1}_video_\d{2}_\d{1}')
                matchobj = regex.match(cam_file.split('/')[-1])
                if matchobj == None:
                    error_file_name.append(cam_file)

                try:
                    f = open(cam_file, 'r', encoding = 'utf-8-sig')
                    rdr = csv.reader(f)

                    ## error_column_name : annotation file dml column 확인 ('start', 'end').
                    for line in rdr:
                        if line[0] != 'start':
                            a = cam_file + ', ' + line[0]
                            error_column_name.append(a)

                        if line[1] != 'end':
                            b = cam_file + ', ' + line[1]
                            error_column_name.append(b)

                        break

                    ## error_other_char : column과 timestamp 이외의 문자 기입 확인.
                    df = pd.read_csv(cam_file, encoding = 'utf-8-sig')
                    size = len(df)
                    for idx in range(size):
                        start = df.loc[idx][0]
                        end = df.loc[idx][1]
                        
                        if (isinstance(start, str) or isinstance(end, str)) == False:
                            break

                        regex = re.compile(r'\d{2}:\d{2}:\d{2}:\d{2}')
                        
                        # 기타 문자 기입 확인. 
                        matchobj = regex.fullmatch(start)
                        matchobj2 = regex.fullmatch(end)

                        if (matchobj == None):
                            a = cam_file
                            error_other_char.append(a)

                        if (matchobj2 == None):
                            b = cam_file
                            error_other_char.append(b)


                    ## error_time_overlap : annotation file 의 timestamp 중복 확인.
                    if cam_file not in error_other_char:
                        df2 = pd.read_csv(cam_file, encoding = 'utf-8-sig')
                        size = len(df2)

                        length = 0
                        for i in range(size):
                            t = df.loc[i][0]
                            if (isinstance (t, str) == False):
                                break
                            length += 1

                        for idx in range(length-1):
                            start = df.loc[idx+1][0]
                            end = df.loc[idx][1]
                            
                            if start == None: 
                                break

                            if time_to_idx(start) <= time_to_idx(end):
                                a = cam_file + ', ' + start
                                error_time_overlap.append(a)

                ## error_cannot_read : annotation file encoding 되지 않는 경우, 예외 처리.
                except:
                    error_cannot_read.append(cam_file)

        else:
            if cam_file[1:2] != 'D':
                error_no_video.append(cam_file)

    with open(os.path.join(args.save_path, 'cam_inspection_result.txt'), 'w', encoding='utf-8', newline='' ) as f:
            
            f.write('Number of CAM files reviewed\n')
            f.write(str(cam_file_cnt))
            f.write('\n\n')

            f.write('Error: error_no_video\n')
            for i in range(len(error_no_video)):
                f.write(error_no_video[i])
                f.write("\n")
            
            f.write("\n")
            f.write('Error: error_file_name\n')
            for i in range(len(error_file_name)):
                f.write(error_file_name[i])
                f.write("\n")

            f.write("\n")
            f.write('Error: error_column_name\n')
            for i in range(len(error_column_name)):
                f.write(error_column_name[i])
                f.write("\n")

            f.write("\n")
            f.write('Error: error_time_overlap\n')
            for i in range(len(error_time_overlap)):
                f.write(error_time_overlap[i])
                f.write("\n")

            f.write("\n")
            f.write('Error: error_other_char\n')
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
    cam_inspection(target_path)

    print("\n\nCOMPLETE!\n\n")


if __name__ == "__main__":
    main()

