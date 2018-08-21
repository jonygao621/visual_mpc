import os
import python_visual_mpc
current_dir = '/'.join(str.split(__file__, '/')[:-1])
bench_dir = '/'.join(str.split(__file__, '/')[:-2])

from python_visual_mpc.visual_mpc_core.algorithm.cem_controller import CEM_controller

ROOT_DIR = os.path.abspath(python_visual_mpc.__file__)
ROOT_DIR = '/'.join(str.split(ROOT_DIR, '/')[:-2])

from python_visual_mpc.visual_mpc_core.agent.general_agent import AgentMuJoCo
import numpy as np

agent = {
    'type': AgentMuJoCo,
    'T': 15,
    'substeps':200,
    'make_final_gif':'',
    'adim':3,
    'sdim':6,
    # 'no_instant_gif':"",
    'filename': ROOT_DIR + '/mjc_models/cartgripper_updown.xml',
    'filename_nomarkers': ROOT_DIR + '/mjc_models/cartgripper_updown.xml',
    'gen_xml':1,   #generate xml every nth trajecotry
    'num_objects': 1,
    'viewer_image_height' : 480,
    'viewer_image_width' : 640,
    'image_height':48,
    'image_width':64,
    'additional_viewer':'',
    'data_save_dir': os.environ['VMPC_DATA_DIR'] + '/mj_pos_noreplan_fast',
    'posmode':"",
    'targetpos_clip':[[-0.45, -0.45, -0.08], [0.45, 0.45, 0.15]],
    'discrete_adim':[2],
    'not_use_images':"",
}

policy = {
    # 'verbose':10,
    'type' : CEM_controller,
    'current_dir':current_dir,
    'nactions': 5,
    'repeat': 3,
    'initial_std': 0.08,        # std dev. in xy
    'initial_std_lift': 1.6,
    'iterations': 2,
    'action_cost_factor': 0,
    'rew_all_steps':"",
    'finalweight':10,
    'no_action_bound':"",
    'num_samples': 100,
    # 'use_first_plan':''
}

tag_images = {'name': 'images',
             'file':'/images/im{}.png',   # only tindex
             'shape':[agent['image_height'],agent['image_width'],3],
               }

tag_qpos = {'name': 'qpos',
             'shape':[3],
             'file':'/state_action.pkl'}
tag_object_full_pose = {'name': 'object_full_pose',
                         'shape':[4,7],
                         'file':'/state_action.pkl'}
tag_object_statprop = {'name': 'obj_statprop',
                     'not_per_timestep':''}

config = {
    'current_dir':current_dir,
    'save_data': False,
    'save_raw_images':'',
    'start_index':0,
    'end_index': 99,
    'agent':agent,
    'policy':policy,
    'ngroup': 1000,
    'sourcetags':[tag_images, tag_qpos, tag_object_full_pose, tag_object_statprop],
    'source_basedirs':[os.environ['VMPC_DATA_DIR'] + '/cartgripper_startgoal_short/train'],
    'sequence_length':2
}