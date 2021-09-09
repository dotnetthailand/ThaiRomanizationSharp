using System.Linq;
using TorchSharp;
using TorchSharp.Modules;
using static TorchSharp.torch;

namespace ThaiRomanizationSharp.Thai2Rom.NeuralNet
{
    using static ThaiRomanizationSharp.Thai2Rom.Extensions;

    internal sealed class Encoder : nn.CustomModule
    {
        private readonly Embedding character_embedding;
        private readonly LSTM rnn;
        private readonly Dropout dropout;
        private (Tensor h0, Tensor c0) hidden;

        public Encoder(long vocabularySize, long embeddingSize, long hiddenSize, float dropout = 0.5f)
            : base(nameof(Encoder))
        {
            this.HiddenSize = hiddenSize;
            this.character_embedding = nn.Embedding(vocabularySize, embeddingSize);
            this.rnn = nn.LSTM(
                inputSize: embeddingSize,
                hiddenSize: hiddenSize / 2,
                bidirectional: true,
                batchFirst: true
            );

            this.dropout = nn.Dropout(dropout);

            RegisterComponents();
        }

        public long HiddenSize { get; set; }

        internal (Tensor sequencesOutput, (Tensor h0, Tensor c0) hidden) Forward(Tensor sequences, int[] sequencesLength)
        {
            // sequences: (batch_size, sequence_length=MAX_LENGTH)
            // sequences_lengths: (batch_size)

            var batchSize = sequences.size(0);
            this.hidden = this.InitHidden(batchSize);

            sequencesLength = sequencesLength.OrderByDescending(i => i).ToArray();

            // The original python code to calculate these two values was quite a bit more general and complex.
            // We're only using this module for Thai transliteration, we can a bit more specialized and simpler.
            var indexSorted = new[] { 0 };
            var indexUnsort = new[] { 0 };

            var indexSortedTensor = torch.tensor(indexSorted);

            sequences = sequences.index_select(0, indexSortedTensor.to(device));

            sequences = this.character_embedding.forward(sequences);
            sequences = this.dropout.forward(sequences);

            // The original python code called pack_padded_sequence, which isn't currently available in TorchSharp. Skipping it.

            var result = this.rnn.forward(sequences, this.hidden);
            var sequencesOutput = result.Item1;
            this.hidden = (result.Item2, result.Item3);

            // The original python code called pad_packed_sequence, which isn't currently available in TorchSharp. Skipping it.

            var indexUnsortTensor = torch.tensor(indexUnsort).to(device);
            sequencesOutput = sequencesOutput.index_select(
                0, indexUnsortTensor.clone().detach()
            );

            return (sequencesOutput, this.hidden);
        }

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
    }
}
