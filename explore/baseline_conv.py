import torch
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
from argparse import ArgumentParser

import warnings
warnings.filterwarnings('ignore')

from nnfabrik.builder import get_data, get_model, get_trainer
import os


def init_loaders(basepath, **kwargs):
    # as filenames, we'll select all 7 datasets
    filenames = [os.path.join(basepath, file) for file in os.listdir(basepath) if ".zip" in file ]

    dataset_fn = 'sensorium.datasets.static_loaders'
    dataset_config = {
        'paths': filenames,
        'normalize': True,
        'include_behavior': False,
        'include_eye_position': False,
        'batch_size': 128,
    }

    dataset_config.update(kwargs)

    dataloaders = get_data(dataset_fn, dataset_config)
    return dataloaders


def init_model(dataloaders):
    model_fn = 'sensorium.models.stacked_core_full_gauss_readout'
    model_config = {'pad_input': False,
                    'layers': 4,
                    'input_kern': 9,
                    'gamma_input': 6.3831,
                    'gamma_readout': 0.0076,
                    'hidden_kern': 7,
                    'hidden_channels': 64,
                    'depth_separable': True,
                    'grid_mean_predictor': {'type': 'cortex',
                                            'input_dimensions': 2,
                                            'hidden_layers': 1,
                                            'hidden_features': 30,
                                            'final_tanh': True},
                    'init_sigma': 0.1,
                    'init_mu_range': 0.3,
                    'gauss_type': 'full',
                    'shifter': False,
                    'stack': -1,
                    }

    model = get_model(model_fn=model_fn,
                      model_config=model_config,
                      dataloaders=dataloaders,
                      seed=42, )
    return model


def main():
    print('started')
    parser = ArgumentParser()
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    seed = args.seed
    basepath = "./notebooks/data/"
    dataloaders = init_loaders(basepath, scale=0.25)
    model = init_model(dataloaders).cuda()


    from sensorium.training import standard_trainer
    validation_score, trainer_output, state_dict = standard_trainer(
        model,
        dataloaders,
        seed=seed,
        max_iter=5,
        verbose=True,
        lr_decay_steps=4,
        avg_loss=False,
        lr_init=0.009,
        track_training=True
    )

    # trainer(model, dataloaders, seed=seed)
    print(validation_score)
    print(trainer_output)
    torch.save(model.state_dict(), f'model_checkpoints/smoll_generalization_model_{seed}.pth')


if __name__ == '__main__':
    main()

