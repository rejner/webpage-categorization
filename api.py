import tensorflow as tf

print(tf.__version__)
print(tf.test.is_gpu_available())
print(tf.test.is_built_with_cuda())
# cuda version
print(tf.test.gpu_device_name())

import torch
print(torch.__version__)
print(torch.cuda.is_available())



class WebCatAPI:
    def __init__(self) -> None:
        pass