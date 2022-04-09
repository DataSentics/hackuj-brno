import argparse
import os

from src.fastai_classificator import fastai_test_classificator



def parse_arguments():
    parser = argparse.ArgumentParser()
    # select all parameters
    parser.add_argument(
        '--path',
        type=os.path.abspath,
        required=True,
        help='Image path to be tested'
        )
    parser.add_argument(
        '--model_path',
        type=os.path.abspath,
        required=True,
        help='Model path')
    return parser.parse_args()


def main():
    # get the args
    args = parse_arguments()

    # and run the pipeline
    prediction = fastai_test_classificator(
        path=args.path,
        model_path=args.model_path,
        )

    print(prediction)


if __name__ == "__main__":
    main()