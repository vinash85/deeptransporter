# MIT License

"""Creates a generator that can feed a stream of data from a file inpt"""
import logging
import numpy as np
import pandas as pd
import os
# from keras import backend as K


DEBUG = False


def normalize(data):
    """
    Perform quantile normalization on a dataframe
    """

    # force data into floats for np calculations
    data = data.astype('float')

    # add a epsilon to the data to adjust for 0 values
    data += 0.001

    # https://stackoverflow.com/questions/37935920/quantile-normalization-on-pandas-dataframe
    data /= np.max(np.abs(data), axis=0)  # scale between [0,1]
    rank_mean = data.stack().groupby(
        data.rank(method='first').stack(dropna=False).astype(int)).mean()
    data = data.rank(method='min').stack(dropna=False).astype(
        int).map(rank_mean).unstack()
    return data


def readFile(input_file):
    data = pd.read_csv(input_file, sep="\t")
    data = data.values

    return data


def processDataLabels(input_file, normalize=True, batch_by_type=False):
    # Read in file
    data = pd.read_csv(input_file, sep="\t")

    # split into data and features
    if batch_by_type:
        features = data.iloc[:, :-3]
        cancertype = data.iloc[:, -3]
        cancertype = cancertype.astype('category')
    else:
        features = data.iloc[:, :-2]

    labels = data.iloc[:, -2:]

    # quantile normalization
    if normalize:
        features = normalize(features)

    # process into a numpy array
    features = features.values
    labels = labels.values

    if batch_by_type:
        return features, labels, cancertype
    else:
        return features, labels, None


def generator_survival(features, labels, cancertype=None, shuffle=True, batch_size=64, batch_by_type=False, normalize=False, dataset_type='non_icb', sort_survival=False):
    """
    Parses the input file and creates a generator for the input file

    Returns:
    num_batches_per_epoch -- The number of batches per epoch based on data size
    input_size -- the dimensions of the input data
    it also sort the survival data
    data_generator() -- the generator function to yield the features and labels
    """

    # np.random.seed(230)
    def create_batches(feat, lab, batch_size, shuffle=True):
        data_size = len(feat)
        num_batches_per_epoch = max(1, int((data_size - 1) / batch_size))
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            feat, lab = feat[shuffle_indices], lab[shuffle_indices]
        batches_curr = []
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = (batch_num + 1) * batch_size
            if batch_num == num_batches_per_epoch - 1:
                end_index = data_size

            temp = (feat[start_index:end_index], lab[start_index:end_index])
            batches_curr.append(temp)

        return batches_curr

    def get_batches():
        if batch_by_type:
            batches = [Xy for type_curr in types for Xy in create_batches(features[cancertype == type_curr], labels[cancertype == type_curr], batch_size, shuffle)]
        else:
            batches = create_batches(features, labels, batch_size, shuffle)
        return batches

    if (batch_by_type):
        if cancertype is None:
            raise NameError("cancertype not found")
        # types = cancertype.dtype.categories
        types = set(cancertype)

    batches = get_batches()
    data_size = len(features)
    num_batches_per_epoch = len(batches)
    input_size = features.shape[1]

    # Sorts the batches by survival time
    def data_generator():
        while True:
            batches = get_batches()
            for X, y in batches:
                # X, y = batch[0]
                # import ipdb
                # ipdb.set_trace()
                if sort_survival:
                    sort_index = (input_size - 3) if dataset_type is 'icb' else 0
                    # this was assuming in icb dataset survival is done through
                    idx = np.argsort(abs(y[:, sort_index]))[::-1]
                    X = X[idx, :]
                    # sort by survival time and take censored data
                    # y = y[idx, 1].reshape(-1, 1)
                    y = y[idx, :]

                yield X, y

    return num_batches_per_epoch, input_size, data_generator()


def generator_simple(features, labels, shuffle=True, batch_size=64):
    """
      Takes features and labels and returns a generator for the features labels

      Returns:
      data_generator() -- the generator function to yield the features and labels
      """

    data_size = len(features)
    num_batches_per_epoch = int((len(features) - 1) / batch_size) + 1
    input_size = features.shape[1]

    # Samples from the data and returns a batch
    def data_generator():
        while True:
            if shuffle:
                shuffle_indices = np.random.permutation(np.arange(data_size))
                shuffled_features = features[shuffle_indices]
                shuffled_labels = labels[shuffle_indices]
            else:
                shuffled_features = features
                shuffled_labels = labels

            for batch_num in range(num_batches_per_epoch):
                start_index = batch_num * batch_size
                end_index = min((batch_num + 1) * batch_size, data_size)
                X, y = shuffled_features[start_index:
                                         end_index], shuffled_labels[start_index: end_index]

                yield X, y

    return num_batches_per_epoch, input_size, data_generator()


def generate_data():
    train = np.random.rand(100, 50)
    label = np.random.rand(100, 2)

    return(train, label)

 # read survival dat


def add2stringlist(prefix, List):
    return [prefix + elem for elem in List]


def fetch_dataloader(prefix, types, data_dir, params, train_optimizer_mask, dataset_type='non_icb', shuffle=True):
    """
    Fetches the DataLoader object for each type in types from data_dir.

    Args:
        types: (list) has one or more of 'train', 'val', 'test' depending on which data is required
        data_dir: (string) directory containing the dataset
        params: (Params) hyperparameters

    Returns:
        data: (dict) contains the DataLoader object for each type in types
    """
    train_optimizer_mask = eval(train_optimizer_mask)
    dataloaders = {}
    name = prefix
    prefix = None  # assume there is no prefix in file names
    if isinstance(prefix, str):
        prefix = prefix + "_"
    else:
        prefix = ""

    for split in ['train', 'val', 'test']:
        if split in types:
            print(prefix)
            path = os.path.join(data_dir, "{}".format(prefix))
            print(path)
            # import ipdb
            # ipdb.set_trace()
            features = readFile(path + "ssgsea_" + split + ".txt")
            # remember survival is no longer survival.
            phenotypes_type = readFile(path + "phenotype_" + split + ".txt")
            phenotypes = phenotypes_type[:, 1:]
            phenotypes = phenotypes.astype(float)

            dl = generator_survival(
                features, phenotypes, batch_by_type=params.batch_by_type, cancertype=phenotypes_type[:, 0], batch_size=params.batch_size, normalize=False, dataset_type=dataset_type, shuffle=shuffle)  # outputs (steps_gen, input_size, generator)

            dataloaders[split] = dl

    return dataloaders, train_optimizer_mask, name


def fetch_dataloader_list(prefix, types, data_dir_list, params, shuffle=True):
    """
    Fetches the DataLoader object for each type in types from data_dir.

    Args:
        types: (list) has one or more of 'train', 'val', 'test' depending on which data is required
        data_dir: (string) file containing directories of datasets
        params: (Params) hyperparameters

    Returns:
        datasets: list of (dict) contains the DataLoader object for each type in types
    """

    data_dirs = pd.read_csv(data_dir_list, sep="\t")
    logging.info("Found {} datasets".format(len(data_dirs)))

    datasets = [fetch_dataloader(row['prefix'], types, row['data_dir'], params, row['train_optimizer_mask'], row['dataset_type'], shuffle=shuffle) for index, row in data_dirs.iterrows()]

    return datasets
