# README

This C# library implements transliteration of Thai text to English characters using machine learning.

For example, "สวัสดี" is transliterated to "sawatdi"

It uses the PyTorch machine learning framework with TorchSharp bindings. It's all C# and (cross-platform) native code; no Python installation is required or Python code is executed.

Somewhat ironically, the library itself is a transliteration from Python to C#. All credit for the original algorithm goes to the [PyThaiNLP](https://github.com/PyThaiNLP/pythainlp).

## Links

- [Main PyThaiNLP repository](https://github.com/PyThaiNLP/pythainlp)
   - [Specific "thai2rom" algorithm that was ported](https://github.com/PyThaiNLP/pythainlp/blob/a1028b5799fd8edd7dc8118e7457a12e60ffc467/pythainlp/transliterate/thai2rom.py)
- [PyTorch Model (python pickle format)](https://raw.githubusercontent.com/artificiala/thai-romanization/master/notebook/thai2rom-pytorch-attn-v0.1.tar)
- [Training jupyter notebook](https://github.com/artificiala/thai-romanization/blob/master/notebook/thai_romanize_pytorch_seq2seq_attention.ipynb)

## Dev Guide

The source code in this repository is quite literally translated from the original Python code to C#. For example, the following is a snippet of the original Python code:

```python
def init_hidden(self, batch_size):
    h_0 = torch.zeros(
        [2, batch_size, self.hidden_size // 2], requires_grad=True
    ).to(device)
    c_0 = torch.zeros(
        [2, batch_size, self.hidden_size // 2], requires_grad=True
    ).to(device)

    return (h_0, c_0)
```

And the corresponding C# code in this repository is:

```csharp
private (Tensor h_0, Tensor c_0) InitHidden(long batchSize)
{
    var h_0 = torch.zeros(
        new[] { 2, batchSize, this.HiddenSize / 2 }, requiresGrad: true
    ).to(device);
    var c_0 = torch.zeros(
        new[] { 2, batchSize, this.HiddenSize / 2 }, requiresGrad: true
    ).to(device);

    return (h_0, c_0);
}
```

Like the underlying TorchSharp library, the C# coding style often departs from C# standard coding style and descriptive variable names, in order to match the original Python code. As improvements are made to the underlying Python code, it's easier to port them to the C#. Please resist the urge to refactor/rename everything.

**ML Models**

PyTorch model files are pickled Python. This is problematic for C#. Luckily, TorchSharp has a conversion process, which is documented [here](https://github.com/dotnet/TorchSharp/blob/decd474288196e8f4119991a69def32f0e106eff/docfx/articles/saveload.md). From the original `thai2rom.py` file, the following Python code can be appended to `ThaiTransliterator.__init__` to produce the files in the `Models/Data/` directory of this project:

```python
# record all model parameters and utilities (but not the models, 'model_state_dict' and 'optimizer_state_dict').
with open('/home/bob/model_parameters.json', 'w+') as f:
    f.write(json.dumps({
        'epoch': loader['epoch'],
        'loss': loader['loss'],
        'char_to_ix': loader['char_to_ix'],
        'ix_to_char': loader['ix_to_char'],
        'target_char_to_ix': loader['target_char_to_ix'],
        'ix_to_target_char': loader['ix_to_target_char'],
        'encoder_params': loader['encoder_params'],
        'decoder_params': loader['decoder_params']
    }))
# convert models to TorchSharp compatible, using https://github.com/dotnet/TorchSharp/blob/main/src/Python/exportsd.py
from pythainlp.transliterate.exportsd import save_state_dict
with open("/home/bob/model_state_dict", "wb") as f:
    save_state_dict(loader["model_state_dict"], f)
```

Note that TorchSharp is working hard to support ONNX format, which PyTorch is also working to support. Once both projects have full support, it should be much easier to share models as ONNX, rather than needing the `exportsd` script above.

