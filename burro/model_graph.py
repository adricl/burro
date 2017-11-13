#!../env/bin/python

"""
model_graph.py

View a graph of predicted vs actual steering angles

Usage:
    model_graph.py --data-dir <DIR>, --model <FILE>, [--mode <MODE>]

Options:
  --data-dir <DIR>      data directory
  --model <FILE>
  --mode <MODE>         either regression or categorical [default: categorical]
"""

import sys
import time

from docopt import docopt

import methods
import config

from trainers.img_pipelines import categorical_pipeline, regression_pipeline
from trainers.generators.pil_generators import show_image
from keras.models import load_model
import pandas as pd
import numpy as np


def main():
    arguments = docopt(__doc__)
    data_dir = arguments['--data-dir']
    print "Data Dir " + data_dir
    model_file = arguments['--model']
    print "Model " + model_file
    mode = arguments['--mode']
    print "Mode " + mode

    if mode == 'regression':
        pipeline = regression_pipeline(data_dir, val_every=10, batch_size=1)
    elif mode == 'categorical':
        pipeline = categorical_pipeline(data_dir, val_every=10, batch_size=1, indefinite=False, graph=True)
    print model_file

    print "Loaded Images"
    model = load_model(model_file)
    #model.summary()
    #print model.to_json()

    # model.compile(
    #     optimizer='adam', loss={
    #         'angle_out': 'categorical_crossentropy',
    #         'throttle_out': 'mean_absolute_error'},
    #         loss_weights={'angle_out': 0.9, 'throttle_out': .001})

    # model.compile(
    #     optimizer='adam', loss={
    #         'angle_out': 'categorical_crossentropy',
    #         },
    #         loss_weights={'angle_out': 0.9})

    prediction = model.predict_generator(pipeline, steps=44, use_multiprocessing=False, verbose=1)
    print "Prediction " + str(len(prediction[0]))
    #print "Values " + values[0]
    #prediction = prediction.reshape((stream.shape[0],))
    #ax = pd.DataFrame({'predicted':prediction, 'actual':values}).plot()
    #ax.set_ylabel("steering angle")




if __name__ == "__main__":
    main()
