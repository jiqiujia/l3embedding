# coding: utf8

import sys
import argparse
import logging
import os
import random
from csv import DictWriter
import glob
from collections import OrderedDict
from log import init_console_logger

LOGGER = logging.getLogger('data')
LOGGER.setLevel(logging.DEBUG)

def write_subset_file(path, subset_list):
    with open(path, 'w') as f:
        field_names = list(subset_list[0].keys())
        writer = DictWriter(f, field_names)
        writer.writeheader()

        for item in subset_list:
            item = dict(item)
            item['labels'] = ';'.join(item['labels'])
            writer.writerow(item)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Creates CSVs containing a train-valid-test split for the given dataset')

    parser.add_argument('-vr',
                        '--valid-ratio',
                        dest='valid_ratio',
                        action='store',
                        type=float,
                        default=0.1,
                        help='Ratio of dataset used for validation set')

    parser.add_argument('-tr',
                        '--test-ratio',
                        dest='test_ratio',
                        action='store',
                        type=float,
                        default=0.1,
                        help='Ratio of dataset used for test set')

    parser.add_argument('-rs',
                        '--random-seed',
                        dest='random_seed',
                        action='store',
                        type=int,
                        default=12345678,
                        help='Random seed used for generating split')

    parser.add_argument('-r',
                        '--random-state',
                        dest='random_state',
                        action='store',
                        type=int,
                        default=20171021,
                        help='Random seed used to set the RNG state')

    parser.add_argument('--video_data_dir',
                        action='store',
                        type=str,
                        help='Path to directory where video data files are stored')

    parser.add_argument('--audio_data_dir',
                        action='store',
                        type=str,
                        help='Path to directory where audio data files are stored')

    parser.add_argument('--output_dir',
                        action='store',
                        type=str,
                        help='Path to directory where output files will be stored')

    parser.add_argument('--filename_prefix',
                        action='store',
                        type=str,
                        help='Path to directory where output files will be stored')

    return parser.parse_args()

def get_filename(path):
    """Return the filename of a path

    Args: path: path to file

    Returns:
        filename: name of file (without extension)
    """
    return os.path.splitext(os.path.basename(path))[0]

if __name__ == '__main__':
    init_console_logger(LOGGER, verbose=True)

    args = parse_arguments()

    video_files = glob.glob(os.path.join(args.video_data_dir, "*.mp4"))
    video_files += glob.glob(os.path.join(args.video_data_dir, "*/*.mp4"))
    audio_files = glob.glob(os.path.join(args.audio_data_dir, "*.wav"))
    print("num of video files {}".format(len(video_files)))
    print("num of audio files {}".format(len(audio_files)))

    video_file_names = set([get_filename(path) for path in video_files])
    audio_file_names = set([get_filename(path) for path in audio_files])

    valid_file_names = video_file_names & audio_file_names
    print("num of valid files {}".format(len(valid_file_names)))

    # Get map from filename to full audio and video paths
    audio_paths = {get_filename(path): path for path in audio_files
                                       if get_filename(path) in valid_file_names}
    video_paths = {get_filename(path): path for path in video_files
                                       if get_filename(path) in valid_file_names}
    file_list = []
    for file_name in valid_file_names:
        item = OrderedDict()
        item['yid'] = file_name
        item['audio_filepath'] = audio_paths[file_name]
        item['video_filepath'] = video_paths[file_name]
        item['labels'] = ['1']

        file_list.append(item)
    logging.info('len of file {}'.format(len(file_list)))

    random.shuffle(file_list)

    # Figure out number of files for each subset
    num_files = len(file_list)
    num_valid = int(num_files * args.valid_ratio)
    num_test = int(num_files * args.test_ratio)

    # Get subset lists
    valid_list = file_list[:num_valid]
    test_list = file_list[num_valid:num_valid+num_test]
    train_list = file_list[num_valid+num_test:]

    output_dir = args.output_dir
    filename_prefix = args.filename_prefix
    train_subset_path = os.path.join(output_dir, filename_prefix + '_train.csv')
    valid_subset_path = os.path.join(output_dir, filename_prefix + '_valid.csv')
    test_subset_path = os.path.join(output_dir, filename_prefix + '_test.csv')

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    write_subset_file(train_subset_path, train_list)
    write_subset_file(valid_subset_path, valid_list)
    write_subset_file(test_subset_path, test_list)
