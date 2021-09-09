using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using ThaiRomanizationSharp.Abstractions;
using ThaiRomanizationSharp.Thai2Rom.Models;
using ThaiRomanizationSharp.Thai2Rom.NeuralNet;
using TorchSharp;
using static TorchSharp.torch;

namespace ThaiRomanizationSharp.Thai2Rom
{
    using static ThaiRomanizationSharp.Thai2Rom.Extensions;

    /// <inheritdoc cref="IThaiRomanizationService"/>
    public sealed class Thai2RomService : IThaiRomanizationService
    {
        private readonly Dictionary<string, int> charToIndex;
        private readonly Dictionary<string, int> targetCharToIndex;
        private readonly Dictionary<string, string> indexToTargetChar;
        private readonly Seq2Seq network;

        public Thai2RomService()
            : this(Loader.LoadParameters()) { }

        internal Thai2RomService(ModelParameters loader)
        {
            var (inputDim, eEmbDim, eHidDim, eDropout) = loader.EncoderParams;
            var (outputDim, dEmbDim, dHidDim, dDropout) = loader.DecoderParams;

            const int maxLength = 100;

            this.charToIndex = loader.CharToIndex;
            this.targetCharToIndex = loader.TargetCharToIndex;
            this.indexToTargetChar = loader.IndexToTargetChar;

            var encoder = new Encoder(inputDim, eEmbDim, eHidDim, eDropout);

            var decoder = new AttentionDecoder(outputDim, dEmbDim, dHidDim, dDropout);

            this.network = new Seq2Seq(
                encoder,
                decoder,
                this.targetCharToIndex["<start>"],
                this.targetCharToIndex["<end>"],
                maxLength
            );

            this.network.load("Models/Data/model_state_dict");
            this.network.Eval();
        }

        /// <inheritdoc cref="IThaiRomanizationService.Romanize(string)"/>
        public string Romanize(string text)
        {
            if (text is null) throw new ArgumentNullException(nameof(text));
            if (text is "") return "";

            return Regex
                .Split(text, "([ก-๛]+)([^ก-๛]+)")
                .Select(run =>
                    run.Length > 0 && (int)run[0] is >= 0xE01 and <= 0xE5b
                        ? RomanizeThai(run)
                        : run
                )
                .StringJoin();
        }

        private string RomanizeThai(string text)
        {
            var input_tensor = this.PrepareSequenceIn(text).view(1, -1);
            var input_length = new[] { text.Length + 1 };

            var targetTensorLogits = this.network.Forward(
                input_tensor, input_length, null, 0
            );

            string[] target;
            if (targetTensorLogits.size(0) == 0)
            {
                target = new[] { "<PAD>" };
            }
            else
            {
                var targetTensor = (
                    targetTensorLogits.squeeze(1).argmax(1)
                    .cpu()
                    .detach()
                    .numpy()
                );
                target = targetTensor.Select(t => this.indexToTargetChar[t.ToString()]).ToArray();
            }
            return string.Join("", target);
        }

        /// <summary>
        /// Prepare input sequence for TorchSharp
        /// </summary>
        private Tensor PrepareSequenceIn(string text)
        {
            var idxs = new List<int>();
            foreach (var ch in text)
            {
                if (this.charToIndex.TryGetValue(ch.ToString(), out var value))
                {
                    idxs.Add(value);
                }
                else
                {
                    idxs.Add(this.charToIndex["<UNK>"]);
                }
            }
            idxs.Add(this.charToIndex["<end>"]);
            var tensor = torch.tensor(idxs, dtype: torch.@long);
            return tensor.to(device);
        }

        public void Dispose() => this.network.Dispose();
    }
}
