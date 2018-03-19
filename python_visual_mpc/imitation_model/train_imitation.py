import tensorflow as tf
from tensorflow.python.platform import flags
import os
import imp

from python_visual_mpc.video_prediction.read_tf_records2 import \
                    build_tfrecord_input as build_tfrecord
if __name__ == '__main__':
    FLAGS = flags.FLAGS
    flags.DEFINE_string('hyper', '', 'hyperparameters configuration file')
    flags.DEFINE_integer('device', 0 ,'the value for CUDA_VISIBLE_DEVICES variable')

def main():
    os.environ["CUDA_VISIBLE_DEVICES"] = str(FLAGS.device)
    print 'using CUDA_VISIBLE_DEVICES=', FLAGS.device
    from tensorflow.python.client import device_lib
    print device_lib.list_local_devices()

    if not os.path.exists(FLAGS.hyper):
        raise RuntimeError("Experiment configuration not found")

    hyperparams = imp.load_source('hyperparams', FLAGS.hyper)
    conf = hyperparams.configuration
    conf['visualize'] = False

    with tf.variable_scope('model', reuse = None) as training_scope:
        data_dict = build_tfrecord(conf, training=True)
        # training input images
        train_images = data_dict['images']
        # training ground truth actions/endef
        train_actions = data_dict['actions']
        train_endeffector_pos = data_dict['endeffector_pos']

        model = conf['model'](conf, train_images, train_actions, train_endeffector_pos)
        model.build()

    with tf.variable_scope('val_model', reuse = None):
        data_dict = build_tfrecord(conf, training=False)
        # validation input images
        val_images = data_dict['images']
        # validation ground truth actions/endef
        val_actions = data_dict['actions']
        val_endeffector_pos = data_dict['endeffector_pos']

        with tf.variable_scope(training_scope, reuse=True):
            val_model = conf['model'](conf, val_images, val_actions, val_endeffector_pos)
            val_model.build()

    if 'clip_grad' not in conf:
        conf['clip_grad'] = 1.0

    optimizer = tf.train.RMSPropOptimizer(conf['learning_rate'], decay=0.95)
    gradients, variables = zip(*optimizer.compute_gradients(model.loss))
    gradients = [tf.clip_by_value(g, -conf['clip_grad'], conf['clip_grad']) for g in gradients]
    train_operation = optimizer.apply_gradients(zip(gradients, variables))


    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)

    vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)
    saver = tf.train.Saver(vars, max_to_keep=0)

    sess = tf.Session(config= tf.ConfigProto(gpu_options=gpu_options))
    tf.train.start_queue_runners(sess)
    sess.run(tf.global_variables_initializer())

    summary_writer = tf.summary.FileWriter(conf['model_dir'], graph=sess.graph, flush_secs=10)

    for i in xrange(conf['n_iters']):
        if i % conf['n_print'] == 0:
            if 'MDN_loss' in conf:
                model_loss, val_model_loss, val_model_diag, val_mdn_log, val_aux,  _ = sess.run(
                    [model.loss, val_model.loss, val_model.diagnostic_l2loss,val_model.MDN_log_l, val_model.final_frame_aux_loss, train_operation])
                print 'At iteration', i, 'model loss is:', model_loss, 'and val_model loss is', val_model_loss, 'and val diagnostic', val_model_diag
                itr_summary = tf.Summary()
                itr_summary.value.add(tag="val_model/loss", simple_value=val_model_loss)
                itr_summary.value.add(tag="val_model/loglikelihood", simple_value=val_mdn_log)
                itr_summary.value.add(tag="val_model/finaleep_loss", simple_value=val_aux)
                itr_summary.value.add(tag="val_model/diagnostic_l2loss", simple_value=val_model_diag)
                itr_summary.value.add(tag="model/loss", simple_value=model_loss)
                summary_writer.add_summary(itr_summary, i)
            else:
                model_loss, val_model_loss, val_action,val_aux,  _ = sess.run([model.loss, val_model.loss,
                                                          val_model.action_loss, val_model.final_frame_aux_loss, train_operation])
                print 'At iteration', i, 'model loss is:', model_loss, 'and val_model loss is', val_model_loss
                itr_summary = tf.Summary()
                itr_summary.value.add(tag="val_model/loss", simple_value=val_model_loss)
                itr_summary.value.add(tag="val_model/action_loss", simple_value=val_action)
                itr_summary.value.add(tag="val_model/finaleep_loss", simple_value=val_aux)
                itr_summary.value.add(tag="model/loss", simple_value=model_loss)
                summary_writer.add_summary(itr_summary, i)
        else:
            sess.run([train_operation])

        if i > 0 and i % conf['n_save'] == 0:
            saver.save(sess, conf['model_dir'] + '/model' + str(i))

    saver.save(sess, conf['model_dir'] + '/modelfinal' + str(i))
    sess.close()



if __name__ == '__main__':
    main()