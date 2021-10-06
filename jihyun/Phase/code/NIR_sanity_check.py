import os
import re
import csv
import glob
import pandas as pd

import argparse 
import natsort

parser = argparse.ArgumentParser()
parser.add_argument('--target_dir_path', type=str, default='/Users/jihyunlee/Desktop/data-preprossing/nir', help='path of target directory')
parser.add_argument('--save_path', type=str, default='/Users/jihyunlee/Desktop/data-preprossing/results', help='inspection result save path')
args = parser.parse_args()


def time_to_idx(time):
    fps = 30
    t_segment = time.split(':')
    idx = int(t_segment[0])*3600 + int(t_segment[1])*60 + int(t_segment[2])
    frame = idx * fps + int(t_segment[3])

    return frame


def nir_inspection(path_dir):
    # nir.csv 파일 리스트
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
    
    nir_file_cnt = 0
    for nir_file in file_list:
        
        flag = 1
        
        if nir_file.split('/')[-1][0:1] == 'R':
            nir_file_cnt += 1
            print('===> {} target annotation file : {} '.format(nir_file_cnt, nir_file))

            '''
            video_dir = os.path.join('/host_server/nas/HUTOM_DATA2/Gastrectomy/YUHS/WJ_Hyung/Videos/Robot/R000', nir_file.split('/')[-1][1:4], 'Videos')
            video_list = os.listdir(video_dir)
            video_list.sort()

            for video_file in video_list:
                if video_file[-6:-4] == nir_file[19:21]:
                    if nir_file[9:12] in video_file:
                        # video_file = video_file
                        flag = 1
                        break
            '''

            ## error_no_video : annotation file 에 해당하는 비디오 없음.
            ## 일치하는 비디오가 없다면, 다른 것은 검사하지도 않는다. 
            if flag == 0:
                error_no_video.append(nir_file)
            
            else:
                ## error_file_name : annotation file 명 포맷 확인 (format : R001_NIR_ch1_video_03_1.csv). 
                if ('ch2' in nir_file) or (' ' in nir_file):
                    error_file_name.append(nir_file)

                regex = re.compile(r'R\d{3}_NIR_ch\d{1}_video_\d{2}_\d{1}')
                matchobj = regex.match(nir_file.split('/')[-1])
                if matchobj == None:
                    error_file_name.append(nir_file)

                try:
                    f = open(nir_file, 'r', encoding = 'utf-8-sig')
                    rdr = csv.reader(f)

                    ## error_column_name : annotation file dml column 확인 ('start', 'end').
                    for line in rdr:
                        if line[0] != 'start':
                            a = nir_file + ', ' + line[0]
                            error_column_name.append(a)

                        if line[1] != 'end':
                            b = nir_file + ', ' + line[1]
                            error_column_name.append(b)

                        break

                    ## error_other_char : column과 timestamp 이외의 문자 기입 확인.
                    df = pd.read_csv(nir_file, encoding = 'utf-8-sig')
                    size = len(df)
                    for idx in range(size):
                        start = df.loc[idx][0]
                        end = df.loc[idx][1]
                        
                        if (isinstance(start, str) or isinstance(end, str)) == False:
                            break

                        regex = re.compile(r'\d{2}:\d{2}:\d{2}:\d{2}')
                        
                        #기타 문자 기입 확인. 
                        matchobj = regex.fullmatch(start)
                        matchobj2 = regex.fullmatch(end)

                        if (matchobj == None):
                            a = nir_file
                            error_other_char.append(a)

                        if (matchobj2 == None):
                            b = nir_file
                            error_other_char.append(b)


                    ## error_time_overlap : annotation file 의 timestamp 중복 확인.
                    if nir_file not in error_other_char:
                        df2 = pd.read_csv(nir_file, encoding = 'utf-8-sig')
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
                                a = nir_file + ', ' + start
                                error_time_overlap.append(a)

                except:
                    error_cannot_read.append(nir_file)

         ## error_cannot_read : annotation file encoding 되지 않는 경우, 예외 처리.
        else:
            if nir_file[1:2] != 'D':
                error_no_video.append(nir_file)


    with open(os.path.join(args.save_path, 'nir_inspection_result.txt'), 'w', encoding='utf-8', newline='' ) as f:

            f.write('Number of NIR files reviewed\n')
            f.write(str(nir_file_cnt))
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
    nir_inspection(target_path)
    
    print("\n\nCOMPLETE!\n\n")


if __name__ == "__main__":
    main()

