"""
Scripts to extract frames from videos with hvat jsons
"""

import json
import datetime
import os
import os.path as osp
from glob import glob
from subprocess import Popen, PIPE


def load_json(json_path):
    """Load json

    Args:
        json_path (str): json file path

    Returns:
        dict: data from json
    """

    with open(json_path, 'r') as read_json:
        json_data = json.load(read_json)
    return json_data


def dump_json(json_data, json_path):
    """Dump json

    Args:
        json_data (dict): dict to save in json format
        json_path (str): file path to save in json
    """

    with open(json_path, 'w') as write_json:
        json.dump(json_data, write_json)


def get_json_list(json_dir):
    """Get a list of json paths

    Args:
        json_dir (str): directory for json files

    Returns:
        list: list of json paths
    """

    json_list = glob(osp.join(json_dir, '*.json'))
    return json_list


def get_ffmpeg_cmds(video_dir, out_dir, json_list):
    """Get commands for extracting frames from json with ffmpeg

    Args:
        video_dir (str): directory for json files
        out_dir (str): directory to save extracted frames
        json_list (list): list of json paths

    Returns:
        list: list of commands to run
    """

    cmds_list = []
    for json_path in json_list:
        json_data = load_json(json_path)
        fps = json_data['frameRate']
        video_name = json_data['name']
        os.makedirs(osp.join(out_dir, video_name), exist_ok=True)
        video_path = '.'.join([osp.join(video_dir, video_name), 'mp4'])
        for ann in json_data['annotations']:
            fnum = ann['start']
            try:
                label = ann['code']
            except KeyError:
                continue
            seconds = fnum / fps
            out_path = osp.join(out_dir, video_name,
                                f'fps{fps}_fnum{fnum}_{label}.jpg')
            cmd = f'ffmpeg -nostdin -ss {seconds} -i {video_path} -vframes 1 {out_path}'
            cmds_list.append([cmd])
    return cmds_list


def wait_proc(cmds_list):
    """Wait until subprocesses will be finished

    Args:
        cmds_list (list): list of commands to run
    """

    procs_list = [
        Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True) for cmd in cmds_list
    ]
    for proc in procs_list:
        proc.wait()

    print('Processes are finished')


if __name__ == '__main__':
    json_dir = '/host_server/nas/ai_shared/CVAT_preprocessing/JSON'
    video_dir = '/host_server/nas/ai_shared/CVAT_preprocessing/VIDEO/Gastrectomy/Dataset1'
    out_dir = f"/host_server/nas/ai_shared/CVAT_upload/{datetime.datetime.now().strftime('%y_%m_%d_%H:%M')}"

    json_list = get_json_list(json_dir)
    cmds_list = get_ffmpeg_cmds(video_dir, out_dir, json_list)
    wait_proc(cmds_list)
