import os
from python_visual_mpc.video_prediction.setup_predictor_towers import setup_predictor
current_dir = os.path.dirname(os.path.realpath(__file__))

import python_visual_mpc
# tf record data location:

# local output directory
OUT_DIR = current_dir + '/modeldata'

from python_visual_mpc.video_prediction.dynamic_rnn_model.alex_model_interface import Alex_Interface_Model
from video_prediction.models.indep_multi_savp_model import IndepMultiSAVPVideoPredictionModel
import video_prediction


base_dir = video_prediction.__file__
base_dir = '/'.join(str.split(base_dir, '/')[:-2])
modeldir = base_dir + '/pretrained_models/sawyer_newenv/long_horizon/'

override_json = {'sequence_length':18,
                 'context_frames': 6}       # of frames before predictions.' ,

configuration = {
'pred_model': Alex_Interface_Model,
'override_json':override_json,
'pred_model_class':IndepMultiSAVPVideoPredictionModel,
'setup_predictor':setup_predictor,
'json_dir':  modeldir + '/view0/model.savp.None',
'pretrained_model':[modeldir + '/view0/model.savp.None/model-300000', modeldir + '/view1/model.savp.None/model-300000'],   # 'filepath of a pretrained model to resume training from.' ,
'sequence_length': override_json['sequence_length'],      # 'sequence length to load, including context frames.' ,
'context_frames': override_json['context_frames'],        # of frames before predictions.' ,
'model': 'appflow',            #'model architecture to use - CDNA, DNA, or STP' ,
'batch_size': 200,
'sdim':5,
'adim':5,
'orig_size':[48,64],
'ndesig':2,
'ncam':2,
}