# Copyright Niantic 2019. Patent Pending. All rights reserved.
#
# This software is licensed under the terms of the Monodepth2 licence
# which allows for non-commercial use only, the full terms of which are made
# available in the LICENSE file.

from __future__ import absolute_import, division, print_function

import os
import sys
import glob
import argparse
import numpy as np
import PIL.Image as pil
import matplotlib as mpl
import matplotlib.cm as cm

import torch
from torchvision import transforms, datasets

import Depth.networks as networks
from Depth.layers import disp_to_depth

class DepthMap(object):

    def __init__(self):
        """Function to predict for a single image or folder of images
        """
        model_name = "mono_640x192"

        if torch.cuda.is_available():
            self.device = torch.device("cuda")

        model_path = os.path.join("Depth/models", model_name)
        print("-> Loading model from ", model_path)
        encoder_path = os.path.join(model_path, "encoder.pth")
        depth_decoder_path = os.path.join(model_path, "depth.pth")

        # LOADING PRETRAINED MODEL
        print("   Loading pretrained encoder")
        self.encoder = networks.ResnetEncoder(18, False)
        loaded_dict_enc = torch.load(encoder_path, map_location=self.device)

        # extract the height and width of image that this model was trained with
        self.feed_height = loaded_dict_enc['height']
        self.feed_width = loaded_dict_enc['width']
        filtered_dict_enc = {k: v for k, v in loaded_dict_enc.items() if k in self.encoder.state_dict()}
        self.encoder.load_state_dict(filtered_dict_enc)
        self.encoder.to(self.device)
        self.encoder.eval()

        print("   Loading pretrained decoder")
        self.depth_decoder = networks.DepthDecoder(
            num_ch_enc=self.encoder.num_ch_enc, scales=range(4))

        loaded_dict = torch.load(depth_decoder_path, map_location=self.device)
        self.depth_decoder.load_state_dict(loaded_dict)

        self.depth_decoder.to(self.device)
        self.depth_decoder.eval()


    def get_depth_map(self, image_path):
        # FINDING INPUT IMAGES
        output_directory = os.path.dirname("../" + image_path)

        # PREDICTING ON EACH IMAGE IN TURN
        with torch.no_grad():
            # Load image and preprocess
            input_image = pil.open(image_path).convert('RGB')
            original_width, original_height = input_image.size
            input_image = input_image.resize((self.feed_width, self.feed_height), pil.LANCZOS)
            input_image = transforms.ToTensor()(input_image).unsqueeze(0)

            # PREDICTION
            input_image = input_image.to(self.device)
            features = self.encoder(input_image)
            outputs = self.depth_decoder(features)

            disp = outputs[("disp", 0)]
            disp_resized = torch.nn.functional.interpolate(
                disp, (original_height, original_width), mode="bilinear", align_corners=False)

            # Saving numpy file
            output_name = os.path.splitext(os.path.basename(image_path))[0]
            name_dest_npy = os.path.join(output_directory, "{}_disp.npy".format(output_name))
            scaled_disp, _ = disp_to_depth(disp_resized, 0.1, 100)
            self.depth_map = scaled_disp.cpu().numpy()
            np.save(name_dest_npy, self.depth_map)

        print('-> Done!')
        return self.depth_map
