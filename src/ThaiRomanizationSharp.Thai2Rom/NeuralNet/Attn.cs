using System;
using TorchSharp.Modules;
using static TorchSharp.torch;
using F = TorchSharp.torch.nn.functional;

namespace ThaiRomanizationSharp.Thai2Rom.NeuralNet
{
    internal sealed class Attn : nn.CustomModule
    {
        private readonly string method;
        private readonly long hiddenSize;
        private readonly Linear attn;

        public Attn(string method, long hiddenSize)
            :base("attn")
        {
            this.method = method;
            this.hiddenSize = hiddenSize;

            if(this.method == "general")
            {
                this.attn = nn.Linear(this.hiddenSize, hiddenSize);
            }
            else// if(this.method == "concat")
            {
                throw new NotImplementedException("not used in original python program");
            }

            RegisterComponents();
        }

        internal Tensor Forward(Tensor hidden, Tensor encoderOutputs, Tensor mask)
        {
            // Calculate energies for each encoder output
            Tensor attnEnergies;
            if(this.method == "dot")
            {
                throw new NotImplementedException("not used in original python program");
            }
            else if (this.method == "general")
            {
                attnEnergies = this.attn.forward(
                    encoderOutputs.view(-1, encoderOutputs.size(-1))
                ); // (batch_size * sequence_len,  hidden_size)
                attnEnergies = attnEnergies
                    .view(encoderOutputs.size())
                    .bmm(
                        hidden.transpose(1, 2))
                    .squeeze(
                        2
                    );
            }
            else// if (this.method == "concat")
            {
                throw new NotImplementedException("not used in original python program");
            }

            attnEnergies = attnEnergies.masked_fill(mask.eq(0), -1e10);

            // Normalize energies to weights in range 0 to 1
            return F.softmax(attnEnergies, 1);
        }
    }
}
