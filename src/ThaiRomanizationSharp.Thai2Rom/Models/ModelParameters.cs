using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace ThaiRomanizationSharp.Thai2Rom.Models
{
    /// <summary>
    /// JSON model of model_parameter.json.
    /// </summary>
    /// <remarks>
    /// The JSON file was extracted from the python-pickled file here:
    /// https://raw.githubusercontent.com/artificiala/thai-romanization/master/notebook/thai2rom-pytorch-attn-v0.1.tar
    /// You can see the python code that produces the python-pickeled file here:
    /// https://github.com/artificiala/thai-romanization/blob/master/notebook/thai_romanize_pytorch_seq2seq_attention.ipynb
    /// </remarks>
    internal sealed class ModelParameters
    {
        [JsonPropertyName("epoch")]
        public int Epoch { get; set; }

        [JsonPropertyName("loss")]
        public float Loss { get; set; }

        [JsonPropertyName("char_to_ix")]
        public Dictionary<string, int> CharToIndex { get; set; } = new();

        [JsonPropertyName("ix_to_char")]
        public Dictionary<string, string> IndexToChar { get; set; } = new();

        [JsonPropertyName("target_char_to_ix")]
        public Dictionary<string, int> TargetCharToIndex { get; set; } = new();

        [JsonPropertyName("ix_to_target_char")]
        public Dictionary<string, string> IndexToTargetChar { get; set; } = new();

        [JsonPropertyName("encoder_params")]
        public float[] EncoderParams { get; set; } = Array.Empty<float>();

        [JsonPropertyName("decoder_params")]
        public float[] DecoderParams { get; set; } = Array.Empty<float>();
    }
}
