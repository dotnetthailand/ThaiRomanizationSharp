using TorchSharp;
using TorchSharp.Modules;
using static TorchSharp.torch;

namespace ThaiRomanizationSharp.Thai2Rom.NeuralNet
{
    internal sealed class AttentionDecoder : nn.CustomModule
    {
        public long HiddenSize { get; set; }

        public long VocabularySize { get; set; }

        private readonly Embedding character_embedding;
        private readonly LSTM rnn;
        private readonly Attn attn;
        private readonly Linear linear;
        private readonly Dropout dropout;

        public AttentionDecoder(long vocabularySize, long embeddingSize, long hiddenSize, float dropout = 0.5f)
            :base(nameof(AttentionDecoder))
        {
            this.VocabularySize = vocabularySize;
            this.HiddenSize = hiddenSize;
            this.character_embedding = nn.Embedding(
                vocabularySize, embeddingSize
            );
            this.rnn = nn.LSTM(
                inputSize: embeddingSize + this.HiddenSize,
                hiddenSize: hiddenSize,
                bidirectional: false,
                batchFirst: true
            );

            this.attn = new Attn(hiddenSize: this.HiddenSize);
            this.linear = nn.Linear(hiddenSize, vocabularySize);

            this.dropout = nn.Dropout(dropout);

            RegisterComponents();
        }

        internal (Tensor x, Tensor hidden, Tensor attnWeights) Forward(Tensor input, Tensor lastHidden, Tensor encoderOutputs, Tensor mask)
        {
            // input: (batch_size, 1)
            // last_hidden: (batch_size, hidden_dim)
            // encoder_outputs: (batch_size, sequence_len, hidden_dim)
            // mask: (batch_size, sequence_len)

            var hidden = lastHidden.permute(1, 0, 2);
            var attnWeights = this.attn.Forward(hidden, encoderOutputs, mask);

            var contextVector = attnWeights.unsqueeze(1).bmm(encoderOutputs);
            contextVector = contextVector.sum(dim: 1); // ok python translation?
            contextVector = contextVector.unsqueeze(1);

            var embedded = this.character_embedding.forward(input);
            embedded = this.dropout.forward(embedded);

            var rnnInput = torch.cat(new[] { contextVector, embedded }, -1);

            var result = this.rnn.forward(rnnInput, (torch.zeros(1, 1, 256), torch.zeros(1, 1, 256) )); // torch will implicitly pass zeros for us in the python version
            var hiddenResult = (result.Item2, result.Item3);
            var output = result.Item1;
            output = result.Item1.view(-1, result.Item1.size(2));

            var x = this.linear.forward(output);

            return (x, hiddenResult.Item1, attnWeights);
        }
    }
}
