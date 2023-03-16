# Lightweight and High-Fidelity End-to-End Text-to-Speech with Multi-Band Generation and Inverse Short-Time Fourier Transform
### *This project is for reference only. Please refer to the original paper and the original project for details.*

## Original Paper Address
- https://arxiv.org/pdf/2210.15975.pdf

### 1. Pre-requisites

0. Python >= 3.6
0. Clone this repository
0. Install python requirements. Please refer [requirements.txt](requirements.txt)
    1. You may need to install espeak first: `apt-get install espeak`
0. Download datasets
    1. Download and extract the [LJ Speech dataset](https://keithito.com/LJ-Speech-Dataset/), then rename or create a link to the dataset folder: `ln -s /path/to/LJSpeech-1.1/wavs DUMMY1`
0. Build Monotonic Alignment Search and run preprocessing if you use your own datasets.
```sh
# Cython-version Monotonoic Alignment Search
cd monotonic_align
mkdir monotonic_align
python setup.py build_ext --inplace
```

### 2. Setting json file in [configs](configs)

| Model | How to set up json file in [configs](configs) | Sample of json file configuration|
| :---: | :---: | :---: |
| iSTFT-VITS | ```"istft_vits": true, ```<br>``` "upsample_rates": [8,8], ``` | ljs_istft_vits.json |
| MB-iSTFT-VITS | ```"subbands": 4,```<br>```"mb_istft_vits": true, ```<br>``` "upsample_rates": [4,4], ``` | ljs_mb_istft_vits.json |
| MS-iSTFT-VITS | ```"subbands": 4,```<br>```"ms_istft_vits": true, ```<br>``` "upsample_rates": [4,4], ``` | ljs_ms_istft_vits.json |

### 3. Training
In the case of MB-iSTFT-VITS training, run the following script
```sh
python train_latest.py -c configs/ljs_mb_istft_vits.json -m ljs_mb_istft_vits

```

After the training, you can check inference audio using [inference.ipynb](inference.ipynb)

## References
- https://github.com/jaywalnut310/vits.git
- https://github.com/rishikksh20/iSTFTNet-pytorch.git
- https://github.com/rishikksh20/melgan.git
- https://github.com/CjangCjengh/tacotron2-japanese.git
- https://github.com/wind4000/vits.git
