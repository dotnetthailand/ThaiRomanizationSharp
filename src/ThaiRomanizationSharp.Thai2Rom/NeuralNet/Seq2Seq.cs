using System;
using System.Diagnostics;
using System.Linq;
using TorchSharp;
using static TorchSharp.torch;

namespace ThaiRomanizationSharp.Thai2Rom.NeuralNet
{
    using static ThaiRomanizationSharp.Thai2Rom.Extensions;

    /// <summary>
    /// Seq2Seq model for translation (https://en.wikipedia.org/wiki/Seq2seq). This is the root or neural net.
    /// </summary>
    /// <remarks>
    /// https://www.youtube.com/watch?v=MqugtGD605k
    /// https://medium.com/@devnag/seq2seq-the-clown-car-of-deep-learning-f88e1204dac3
    /// https://www.youtube.com/watch?v=sQUqQddQtB4&t=449s
    /// </remarks>
    internal sealed class Seq2Seq : nn.CustomModule
    {
        private readonly Encoder encoder;
        private readonly AttentionDecoder decoder;
        private readonly int padIndex;
        private readonly int targetStartToken;
        private readonly int targetEndToken;
        private readonly int maxLength;
        private readonly Random random;

        public Seq2Seq(Encoder encoder, AttentionDecoder decoder, int targetStartToken, int targetEndToken, int maxLength)
            :base(nameof(Seq2Seq))
        {
            this.encoder = encoder;
            this.decoder = decoder;
            this.padIndex = 0;
            this.targetStartToken = targetStartToken;
            this.targetEndToken = targetEndToken;
            this.maxLength = maxLength;
            this.random = new Random();

            Debug.Assert(encoder.HiddenSize == decoder.HiddenSize);

            this.to(device);

            RegisterComponents();
        }

        internal Tensor Forward(
            Tensor sourceSeq, int[] sourceSeqLen, Tensor? targetSeq, float teacherForcingRatio = 0.5f)
        {
            // source_seq: (batch_size, MAX_LENGTH)
            // source_seq_len: (batch_size, 1)
            // target_seq: (batch_size, MAX_LENGTH)

            var batchSize = sourceSeq.size(0);
            var startToken = this.targetStartToken;
            var endToken = this.targetEndToken;
            var maxLen = this.maxLength;
            var targetVocabSize = this.decoder.VocabularySize;

            var outputs = torch.zeros(maxLen, batchSize, targetVocabSize).to(
                device
            );

            bool inference;
            if(targetSeq is null)
            {
                Debug.Assert(teacherForcingRatio == 0, "Must be zero during inference");
                inference = true;
            }
            else
            {
                inference = false;
            }

            var (encoderOutputs, encoderHidden) = this.encoder.Forward(
                sourceSeq, sourceSeqLen
            );

            var decoderInput = (
                torch.tensor(Enumerable.Repeat(startToken, (int)batchSize).ToArray())
                .view(batchSize, 1)
                .to(device)
            );

            var encoderHiddenHT = torch.cat(
                new[] { encoderHidden.h0[0], encoderHidden.h0[1] }, dimension: 1
            ).unsqueeze(dim: 0);
            var decoderHidden = encoderHiddenHT;

            var maxSourceLen = encoderOutputs.size(1);
            var mask = this.CreateMask(sourceSeq[TensorIndex.Colon, TensorIndex.Slice(0, maxSourceLen)]);

            foreach(var di in Enumerable.Range(0, maxLen))
            {
                (var decoderOutput, decoderHidden, _) = this.decoder.Forward(
                    decoderInput, decoderHidden, encoderOutputs, mask
                );

                var (topv, topi) = decoderOutput.topk(1);
                outputs[di].SetBytes(decoderOutput.to(device).Bytes()); // outputs[di] = decoderOutput seems like it should work, but it throws.

                var teacherForce = random.NextDouble() < teacherForcingRatio;

                decoderInput = (
                    teacherForce
                        ? targetSeq[TensorIndex.Colon, TensorIndex.Single(di)].reshape(batchSize, 1)
                        : topi.detach()
                );

                if(inference && (decoderInput == endToken).ToBoolean())
                {
                    return outputs[TensorIndex.Slice(start: null, di)];
                }
            }

            return outputs;
        }

        private Tensor CreateMask(Tensor sourceSeq)
        {
            var mask = sourceSeq != this.padIndex;
            return mask;
        }
    }
}
