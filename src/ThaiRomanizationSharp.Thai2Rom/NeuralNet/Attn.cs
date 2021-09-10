using TorchSharp.Modules;
using static TorchSharp.torch;
using F = TorchSharp.torch.nn.functional;

namespace ThaiRomanizationSharp.Thai2Rom.NeuralNet
{
    /// <remarks>
    /// The original Attn implementation supported several "methods", but only used the "general" method.
    /// We only ported the "general" method.
    /// </remarks>
    internal sealed class Attn : nn.CustomModule
    {
        private readonly long hiddenSize;
        private readonly Linear attn;

        public Attn(long hiddenSize)
            : base("attn")
        {
            this.hiddenSize = hiddenSize;

            this.attn = nn.Linear(this.hiddenSize, hiddenSize);

            RegisterComponents();
        }

        internal Tensor Forward(Tensor hidden, Tensor encoderOutputs, Tensor mask)
        {
            // Calculate energies for each encoder output
            Tensor attnEnergies;

            attnEnergies = this.attn.forward(
                encoderOutputs.view(-1, encoderOutputs.size(-1))
            ); // shape is (batch_size * sequence_len,  hidden_size)

            attnEnergies = attnEnergies
                .view(encoderOutputs.size())
                .bmm(
                    hidden.transpose(1, 2))
                .squeeze(
                    2
                );

            attnEnergies = attnEnergies.masked_fill(mask.eq(0), -1e10);

            // Normalize energies to weights in range 0 to 1
            return F.softmax(attnEnergies, 1);
        }
    }
}
