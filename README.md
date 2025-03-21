# Sign-IDD
Source code for "Sign-IDD: Iconicity Disentangled Diffusion for Sign Language Production" (Shengeng Tang, Jiayi He, Dan Guo, Yanyan Wei, Feng Li, Richang Hong - AAAI 2025)

# Usage
Install required packages using the requirements.txt file.
```text
pip install -r requirements.txt
```
# Data
PHOENIX14T

We use the same data as the [Progressive Transformer](https://github.com/BenSaunders27/ProgressiveTransformersSLP/tree/master/Data/tmp).

USTC-CSL

Dataset will be released soon.


# Training
```text
python __main__.py train ./Configs/Sign-IDD.yaml
```

# Inference
```text
python __main__.py test ./Configs/Sign-IDD.yaml
```

# Reference
If you use this code in your research, please cite the following [papers](https://arxiv.org/abs/2412.13609):

```bibtex
@article{tang2024sign,
  title={Sign-IDD: Iconicity Disentangled Diffusion for Sign Language Production},
  author={Tang, Shengeng and He, Jiayi and Guo, Dan and Wei, Yanyan and Li, Feng and Hong, Richang},
  journal={arXiv preprint arXiv:2412.13609},
  year={2024}
}

@inproceedings{saunders2020progressive,
	title={{Progressive Transformers for End-to-End Sign Language Production}},
	author={Saunders, Ben and Camgoz, Necati Cihan and Bowden, Richard},
	booktitle={Proceedings of the European Conference on Computer Vision (ECCV)},
	year={2020}
}
```


# Acknowledge
This work was supported by the National Natural Science Foundation of China (Grants No. U23B2031, 61932009, U20A20183, 62272144, 62302141, 62331003), the Anhui Provincial Natural Science Foundation, China (Grant No. 2408085QF191), the Major Project of Anhui Province (Grant No. 202423k09020001), and the Fundamental Research Funds for the Central Universities (Grants No. JZ2024HGTA0178, JZ2024HGTB0255).
