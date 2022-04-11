import argparse
import os

from src.fastai_classificator import fastai_train_classificator


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def parse_arguments():
    parser = argparse.ArgumentParser()
    # select all parameters
    parser.add_argument(
        '--path',
        type=os.path.abspath,
        required=True,
        help='Folder path to the dataset'
        )
    parser.add_argument(
        '--output_path',
        type=os.path.abspath,
        required=True,
        help='Output path for saving stuff')
    return parser.parse_args()


def main():
    # get the args
    args = parse_arguments()

    # and run the pipeline
    fastai_train_classificator(
        path=args.path,
        output_path=args.output_path
        )


if __name__ == "__main__":
    main()