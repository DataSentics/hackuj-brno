from fastbook import *
from fastai.vision.widgets import *
import os


# parameters
batch_size = 128
epoch_num = 20
arch = resnet34  # resnet18, resnet34, resnet50, resnet101, ...
valid_pct = 0.2
crop_size = 224
lr = 1e-3

# augmentations
tfms_do_flip = True
tfms_flip_vert = True
tfms_max_rotate = 50 
tfms_max_zoom = 1.1
tfms_max_warp = 0.2
tfms_max_lighting = 0.5 # max brightness
tfms_p_affine = 0.75 # no random rotation



def create_folder(path, name="models", into_folder=False):
    """Creating folder if does not exist"""
    if into_folder:
        folder_path = os.path.join(Path(path).parents[0], name)
    else:
        folder_path = os.path.join(path, name)
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    return folder_path


def get_augmentations():
    """Get augmentations"""
    return aug_transforms(
        do_flip=tfms_do_flip,
        flip_vert=tfms_flip_vert,
        max_rotate=tfms_max_rotate,
        max_zoom=tfms_max_zoom,
        max_lighting=tfms_max_lighting,
        p_affine=tfms_p_affine,
        max_warp=tfms_max_warp)


def build_datablock(augs):
    """Create datablock for training"""
    return DataBlock(
        blocks=(ImageBlock, CategoryBlock), 
        get_items=get_image_files, 
        splitter=RandomSplitter(valid_pct=valid_pct, seed=242),
        get_y=parent_label,
        item_tfms=RandomResizedCrop(crop_size, min_scale=1),
        batch_tfms=augs)


def create_report_and_save(learn, output_path):

    # training report
    interp = ClassificationInterpretation.from_learner(learn)
    #plot = interp.plot_confusion_matrix(return_fig=True)

    # get folder path
    #folder_path = create_folder(output_path, Path(output_path).name + "_draw")
    folder_path = create_folder(output_path)

    # saving report and model
    learn.export(os.path.join(folder_path, "model"))


def fastai_train_classificator(path, output_path):
    """FastAI training classificator"""

    # get augmentations
    augs = get_augmentations()

    # build datablock for training
    pages = build_datablock(augs)

    # getting dataloaders
    dls = pages.dataloaders(path, batch_size=batch_size)

    # setting up learner
    learn = cnn_learner(dls, arch, metrics=error_rate)

    # training
    learn.fit_one_cycle(epoch_num, lr)

    # creating report and saving report and model
    create_report_and_save(learn, output_path)


def fastai_test_classificator(path, model_path):
    """Run inference on input image path by given model"""

    # load the model
    model = load_learner(model_path)

    # return the inferenced value
    return model.predict(path)
