import torch
import numpy as np
import os
import librosa
from preprocess import wav_padding, world_decompose
from utils import normalize_mccs

def data_load(batchsize = 1, 
              s = -1, 
              t = -1, 
              nb_label=4, 
              data_dir='', 
              voice_dir_list={}, 
              n_frames=1024,
              sampling_rate=16000,
              frame_period=5.0,
              num_mcep=36):
    x = []
    label = []
    for i in range(batchsize):
        if (s == -1):
            label_num = np.random.randint(nb_label)
        else:
            label_num = s
        voice_path = os.path.join(data_dir, voice_dir_list[label_num])
        files = os.listdir(voice_path)
        
        frames = 0
        while frames < n_frames:
            
            file = ""
            while file.count("wav") == 0:
                file = np.random.choice(files)
            wav, _ = librosa.load(os.path.join(voice_path, file), sr = sampling_rate, mono = True)
            wav = librosa.util.normalize(wav, norm=np.inf, axis=None)
            wav = wav_padding(wav = wav, sr = sampling_rate, frame_period = frame_period, multiple = 4)
            f0, timeaxis, sp, ap, mc = world_decompose(wav = wav, fs = sampling_rate, frame_period = frame_period, num_mcep = num_mcep)
            
            mc_transposed  = np.array(mc).T
            frames = np.shape(mc_transposed)[1]
            
        mcep_normalization_params = np.load(os.path.join(voice_path, "mcep_"+voice_dir_list[label_num]+".npz"))
        mcep_mean = mcep_normalization_params['mean']
        mcep_std = mcep_normalization_params['std']
        mc_norm = (mc_transposed  - mcep_mean) / mcep_std
            
        start_ = np.random.randint(frames - n_frames + 1)
        end_ = start_ + n_frames
            
        x.append(mc_norm[:,start_:end_])
        label.append(label_num)

    return torch.Tensor(x).view(batchsize, 1, num_mcep, n_frames), torch.Tensor(label)

def data_load_preprocessed(batchsize = 1, 
              s = -1, 
              t = -1, 
              nb_label=4, 
              data_dir='', 
              data_npy_dir = '',
              voice_dir_list={}, 
              n_frames=1024,
              sampling_rate=16000,
              frame_period=5.0,
              num_mcep=36):
    x = []
    label = []
    for i in range(batchsize):
        if (s == -1):
            label_num = np.random.randint(nb_label)
        else:
            label_num = s
        voice_path = os.path.join(data_dir, voice_dir_list[label_num])
        voice_path_npy = os.path.join(data_npy_dir, voice_dir_list[label_num])
        files = os.listdir(voice_path_npy)
        
        frames = 0
        while frames < n_frames:
            
            file = ""
            while file.count("npy") == 0:
                file = np.random.choice(files)
            mc_transposed  = np.load(os.path.join(voice_path_npy, file))
            frames = mc_transposed.shape[1]
            #print(frames, os.path.join(voice_path_npy, file))

        
        #mcep_normalization_params = np.load(os.path.join(voice_path, "mcep_"+voice_dir_list[label_num]+".npz"))
        #mcep_mean = mcep_normalization_params['mean']
        #mcep_std = mcep_normalization_params['std']
        #mc_norm = (mc_transposed  - mcep_mean) / mcep_std
        norm_coefs_path = os.path.join(voice_path, "mcep_"+voice_dir_list[label_num]+".npz")
        mc_norm = normalize_mccs(mc_transposed, norm_coefs_path)   
        start_ = np.random.randint(frames - n_frames + 1)
        end_ = start_ + n_frames
            
        x.append(mc_norm[:,start_:end_])
        label.append(label_num)

    return torch.Tensor(x).view(batchsize, 1, num_mcep, n_frames), torch.Tensor(label)