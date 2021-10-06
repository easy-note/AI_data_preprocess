import os
import itertools
import argparse

from collections import defaultdict

import openpyxl
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', type=str, help='path of target directory')
args = parser.parse_args()

def ab_grading_inspection():

    base_path = '/Users/jihyunlee/Desktop/bleeding_data_preprosessing/'
    error_column = []
    error_channel = []
    error_row_count = []
    error_except = []
    file_cnt = 0

    for root, dirs, files in os.walk(base_path + 'Individual_to_Consensus_08'):
        files.sort()
        patients_dict = defaultdict(list)
        
        for fname in files:
            if ('Store' in fname) or ('~' in fname):
                continue

            file_cnt += 1

            # patients_dict[fname[:4]].append(fname)
            patients_dict[fname[10:13]].append(fname)
            patients_list = list(patients_dict.values())

            print(patients_list)

            full_fname = os.path.join(root, fname)
            wb = openpyxl.load_workbook(full_fname, data_only=True, read_only=True)
            for worksheet in wb.worksheets:
                sheet = wb[worksheet.title]
                full_fname_sheet = full_fname + ', ' + worksheet.title
                
                try:
                    if sheet['A1'].value.lower() != 'location (x,y)':
                        print('a1')
                        print(full_fname_sheet)
                        error_column.append(full_fname_sheet)
                        break
                    if sheet['G1'].value != None:
                        print('g1')
                        error_column.append(full_fname_sheet)
                        break
                    if sheet['H1'].value.lower() != 'timestamp':
                        print('h1')
                        error_column.append(full_fname_sheet)
                        break
                    if sheet['J1'].value.lower() != 'site':
                        print('j1')
                        error_column.append(full_fname_sheet)
                        break
                    if sheet['L1'].value.lower() != 'cause':
                        print('l1')
                        error_column.append(full_fname_sheet)
                        break
                    if sheet['N1'].value.lower() != 'characteristics':
                        print('n1')
                        error_column.append(full_fname_sheet)
                        break
                    if sheet['Q1'].value.lower() != 'identical':
                        print('q1')
                        print(full_fname_sheet)
                        error_column.append(full_fname_sheet)
                        break
                    if sheet['R1'].value.lower() != 'comment':
                        print('r1')
                        error_column.append(full_fname_sheet)
                        break
                    if 'remedy' not in sheet['S1'].value.lower():
                        print('s1')
                        error_column.append(full_fname_sheet)
                        break
                    if 'remedy' not in sheet['V1'].value.lower():
                        print('v1')
                        error_column.append(full_fname_sheet)
                        break
                    if 'remedy' not in sheet['Y1'].value.lower():
                        print('y1')
                        error_column.append(full_fname_sheet)
                        break
                    if 'remedy' not in sheet['AB1'].value.lower():
                        print('ab1')
                        error_column.append(full_fname_sheet)
                        break
                    if 'remedy' not in sheet['AE1'].value.lower():
                        print('ae1')
                        error_column.append(full_fname_sheet)
                        break
                except:
                    error_column.append(full_fname_sheet)

        
        for patients in patients_list:
            print(patients)
            channel = []
            row = []
            for patient in patients:
                try:
                    dummy_channel = []
                    dummy_row = []
                    full_name = os.path.join(root, patient)
                    wb = openpyxl.load_workbook(full_name, data_only=True, read_only=True)

                    for worksheet in wb.worksheets:
                        dummy_channel.append(worksheet.title)
                        sheet = wb[worksheet.title]

                        df_from_excel = pd.read_excel(full_name,
                                        sheet_name = sheet.title
                                        )

                        dummy_row.append(len(df_from_excel))
                    
                    channel.append(dummy_channel)
                    row.append(dummy_row)
                except:
                    error_except.append(patient[:4])

            try:
                if channel[0] != channel[1]:
                    error_channel.append(patient[:4])

                if row[0] != row[1]:
                    error_row_count.append(patient)
            except:
                error_except.append(patient[:4])



    with open(base_path + 'AB_grading_inspection_08.txt', 'w', encoding='utf-8', newline='' ) as f:

        f.write('Number of ab files reviewed\n')
        f.write(str(file_cnt))
        f.write('\n\n')
        
        f.write('Error: error_column\n')
        for i in range(len(error_column)):
            f.write(error_column[i])
            f.write("\n")
        f.write('\n\n')

        f.write('Error: error_channel\n')
        for i in range(len(error_channel)):
            f.write(error_channel[i])
            f.write("\n")
        f.write('\n\n')

        f.write('Error: error_row_count\n')
        for i in range(len(error_row_count)):
            f.write(error_row_count[i])
            f.write("\n")
        f.write('\n\n')

        f.write('Error: error_except\n')
        for i in range(len(error_except)):
            f.write(error_except[i])
            f.write("\n")
        

# def main():
#     target_path = args.path
#     ab_grading_inspection(target_path)

if __name__ == "__main__":
    ab_grading_inspection()