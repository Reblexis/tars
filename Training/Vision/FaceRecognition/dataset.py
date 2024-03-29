from Training.Vision.FaceRecognition.face_recognition_hyperparameters import *
from Training.training_constants import *
from DataManagement.file_system import load_file, save_to_file
from Training.Extractors.index_extractor import IndexExtractor

import math
import random
from torch.utils.data import Dataset
import torch
import torchvision
import numpy as np


class SiameseDataset(Dataset):
    def __init__(self, dataset: Path, input_transformer: torch.nn.Module,
                 dataset_type: int, seed: int = 1, use_cache: bool = True, dataset_size: int = 12800):
        self.input_transformer = input_transformer

        # Cache
        self.use_cache = use_cache
        self.cache = dict()

        # Loading and filtering dataframe
        if dataset_type != -1:
            self.samples_df = load_file(dataset / DATASET_SAMPLES_DF)

            self.samples_df = self.samples_df.sample(frac=1, random_state=seed)  # shuffle

            self.evaluation_df = load_file(EVALUATION_SAMPLES_DF)
            or_length = len(self.samples_df)
            keys = list(self.samples_df.columns.values)
            i1 = self.samples_df.set_index(keys).index
            i2 = self.evaluation_df.set_index(keys).index
            self.samples_df = self.samples_df[~i1.isin(i2)]

            print(f"Filtered total of: {or_length - len(self.samples_df)} files!")
        else:
            self.samples_df = load_file(EVALUATION_SAMPLES_DF)

        # Create list of paths for each person separately
        people = self.samples_df["person_id"].unique()

        # Select only first 100 people
        self.paths = []
        for person in people:
            self.paths.append(list(self.samples_df[self.samples_df["person_id"] == person]["path"]))

        # Train / test split
        if dataset_type != -1:
            self.dataset_size = math.floor(dataset_size * (TRAIN_TEST_SPLIT[dataset_type + 1] -
                                                           TRAIN_TEST_SPLIT[dataset_type]))
            num_people = len(people)
            self.paths = self.paths[math.floor(TRAIN_TEST_SPLIT[dataset_type] * num_people): math.floor(
                TRAIN_TEST_SPLIT[dataset_type + 1] * num_people)]
        else:
            self.dataset_size = dataset_size

    def preprocess_sample(self, sample_paths: list):
        sample = torch.stack(
            [self.input_transformer((torchvision.io.read_image(path)).type(torch.float32)) for path in
             sample_paths])
        sample /= 255
        return sample

    def save_processed_sample(self, item: int, sample: torch.tensor, label: torch.tensor):
        if self.use_cache:
            self.cache[item] = (sample, label)
        else:
            self.cache[item] = label
            save_to_file(sample, PREPROCESSED_SAMPLES_FOLDER / f"{item}.pt")

    def load_processed_sample(self, item: int):
        if self.use_cache:
            return self.cache[item]
        else:
            return load_file(PREPROCESSED_SAMPLES_FOLDER / f"{item}.pt"), self.cache[item]

    def __len__(self):
        return self.dataset_size

    def __getitem__(self, item):
        if item not in self.cache:
            different_person = np.random.randint(0, 2)
            if different_person:
                people = np.random.choice(len(self.paths), 2, replace=False)
                paths = [random.choice(self.paths[people[0]]), random.choice(self.paths[people[1]])]
            else:
                person = np.random.randint(0, len(self.paths))
                paths = [random.choice(self.paths[person]), random.choice(self.paths[person])]
            y = torch.tensor([different_person], dtype=torch.float32)
            x = self.preprocess_sample(paths)
            self.save_processed_sample(item, x, y)
        else:
            x, y = self.load_processed_sample(item)
        return x, y
