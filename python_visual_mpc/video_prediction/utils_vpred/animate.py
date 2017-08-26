import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import matplotlib.gridspec as gridspec

import matplotlib
import pdb
import cPickle
from scrollable_window import ScrollableWindow

t = 0
class Visualizer(object):
    # def __init__(self, conf, file_path, name= "", examples = 4, show_parts=False):
    def __init__(self, append_masks = True):

        dict_ = cPickle.load(open(file_path + '/pred.pkl', "rb"))
        gen_images = dict_['gen_images']

        self.num_ex = 4
        self.video_list = []

        if 'ground_truth' in dict_:
            ground_truth = dict_['ground_truth']
            if not isinstance(ground_truth, list):
                ground_truth = np.split(ground_truth, ground_truth.shape[1], axis=1)
                ground_truth = [np.squeeze(g) for g in ground_truth]
            ground_truth = ground_truth[1:]

            self.video_list.append((ground_truth, 'Ground Truth'))

        self.video_list.append((gen_images, 'Gen Images'))

        if 'gen_distrib' in dict_:
            gen_pix_distrib = dict_['gen_distrib']
            self.video_list.append((gen_pix_distrib, 'Gen distrib'))

        if append_masks:
            gen_masks = dict_['gen_masks']
            gen_masks = convert_to_videolist(gen_masks, repeat_last_dim=False)

            for i,m in enumerate(gen_masks):
                self.video_list.append((m,'mask {}'.format(i)))

        # if 'flow_vectors' in dict_:
        #     self.videolist.append(visualize_flow(dict_))

        self.build_figure()
        self.t = 0


    def build_figure(self):

        # plot each markevery case for linear x and y scales
        standard_size = np.array([6, 24])
        figsize = (standard_size*1.0).astype(np.int)
        fig = plt.figure(num=1, figsize=figsize)
        axes_list = []

        self.num_rows = len(self.video_list)

        l = []

        for vid in self.video_list:
            l.append(len(vid[0]))
        tlen = np.min(np.array(l))
        print 'minimum video length',tlen

        outer_grid = gridspec.GridSpec(self.num_rows, 1)

        drow = 1./self.num_rows

        self.im_handle_list = []
        for row in range(self.num_rows):
            # outer_ax = fig.add_subplot(outer_grid[row])
            # if self.row_list[row][1] != '':
            #     outer_ax.set_title(self.row_list[1])

            inner_grid = gridspec.GridSpecFromSubplotSpec(1, self.num_ex,
                              subplot_spec=outer_grid[row], wspace=0.0, hspace=0.0)

            image_row = self.video_list[row][0]

            im_handle_row = []
            for col in range(self.num_ex):
                ax = plt.Subplot(fig, inner_grid[col])
                ax.set_xticks([])
                ax.set_yticks([])
                axes_list.append(fig.add_subplot(ax))
                # if row==0:
                #     axes_list[-1].set_title('example {}'.format(col))

                if image_row[0][col].shape[-1] == 1:
                    im_handle = axes_list[-1].imshow(np.squeeze(image_row[0][col]),
                                                     zorder=0, cmap=plt.get_cmap('jet'),
                                                     interpolation='none',
                                                     animated=True)
                else:
                    im_handle = axes_list[-1].imshow(image_row[0][col], interpolation='none',
                                                     animated=True)

                im_handle_row.append(im_handle)
            self.im_handle_list.append(im_handle_row)

            plt.figtext(.5, 1-(row*drow*0.995)-0.005, self.video_list[row][1], va="center", ha="center", size=15)

        plt.axis('off')
        fig.tight_layout()



        # initialization function: plot the background of each frame

        # Set up formatting for the movie files
        Writer = animation.writers['imagemagick_file']
        writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(fig, animate,
                                       fargs= [self.im_handle_list, self.video_list, self.num_ex, self.num_rows, tlen],
                                       frames=tlen, interval=100, blit=True)
        # anim.save('basic_animation.gif', writer='imagemagick')

        a = ScrollableWindow(fig)
        # plt.show()

def animate(*args):
    global t
    _, im_handle_list, video_list, num_ex, num_rows, tlen = args

    artistlist = []
    for row in range(num_rows):
        image_row = video_list[row][0]
        for col in range(num_ex):
            if image_row[0][col].shape[-1] == 1:
                im_handle_list[row][col].set_array(np.squeeze(image_row[t][col]))
            else:
                im_handle_list[row][col].set_array(image_row[t][col])
        artistlist += im_handle_list[row]

    print 'update at t', t
    t += 1

    if t == tlen:
        t = 0

    return artistlist

def convert_to_videolist(input, repeat_last_dim):
    tsteps = len(input)
    nmasks = len(input[0])

    list_of_videos = []

    for m in range(nmasks):  # for timesteps
        video = []
        for t in range(tsteps):
            if repeat_last_dim:
                single_mask_batch = np.repeat(input[t][m], 3, axis=3)
            else:
                single_mask_batch = input[t][m]
            video.append(single_mask_batch)
        list_of_videos.append(video)

    return list_of_videos


if __name__ == '__main__':
    file_path = '/home/frederik/Documents/catkin_ws/src/visual_mpc/tensorflow_data/sawyer/1stimg_bckgd_cdna/modeldata'
    v  = Visualizer()