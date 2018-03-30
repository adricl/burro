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
from config import config

from trainers.img_pipelines import categorical_pipeline, regression_pipeline
from trainers.generators.pil_generators import show_image
from keras.models import load_model
import pandas as pd
import matplotlib.pyplot as plt
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
    im_count = pipeline.file_count(data_dir)
    actual = []
    estimate = []

    for item in pipeline:
        prediction = model.predict(item[0])

    #predictions = model.predict_generator(pipeline, steps=im_count, use_multiprocessing=False, verbose=1)
    #for prediction in predictions:
        
        if len(prediction) == 2:
            yaw_binned = prediction[0]
            throttle = prediction[1][0][0]
        else:
            yaw_binned = prediction
            throttle = 0

        yaw = methods.from_one_hot(yaw_binned)

        # avf = config.model.average_factor
        # yaw = (1.0 - avf) * yaw
        # throttle = throttle * 0.15

        estimate.append(methods.from_one_hot(item[1]))
        actual.append(yaw)
        #print "Predicted Angle " + str(yaw) + " Real Angle " + str(methods.from_one_hot(item[1]))

    #print "Prediction " + str(len(prediction[0]))
    #print "Values " + values[0]
    #prediction = prediction.reshape((stream.shape[0],))
    print "Finished Processing..."
    ax = pd.DataFrame({'predicted':estimate[:100], 'actual':actual[:100]}).plot()
    
    df = ax.plot(kind='scatter', x='predicted', y='actual')
    #df.set_ylabel("steering angle")
    #df.plot()
    plt.savefig('output.png')




if __name__ == "__main__":
    main()
