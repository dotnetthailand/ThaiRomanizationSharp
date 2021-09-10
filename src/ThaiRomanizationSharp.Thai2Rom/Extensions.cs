using System;
using System.Collections.Generic;
using TorchSharp;
using static TorchSharp.torch;

namespace ThaiRomanizationSharp.Thai2Rom
{
    static class Extensions
    {
        /// <summary>
        /// torchsharp doesn't support numpy(), which is the normal way of
        /// getting non-scalar data out of tensors. This is a workaround
        /// until they support it. This is not a general-purpose replacement
        /// </summary>
        public static byte[] numpy(this Tensor tensor) =>
            Array.FindAll(tensor.Bytes().ToArray(), i => i > 0);

        /// <summary>
        /// Special-purpose deconstructing of <see cref="Models.ModelParameters.EncoderParams"/>
        /// and <see cref="Models.ModelParameters.DecoderParams"/>.
        /// </summary>
        public static void Deconstruct(this float[] arr, out long e0, out long e1, out long e2, out float e3)
        {
            e0 = (long)arr[0];
            e1 = (long)arr[1];
            e2 = (long)arr[2];
            e3 = arr[3];
        }

        public static string StringJoin(this IEnumerable<string> sequence, string delimiter = "") =>
            string.Join(delimiter, sequence);

        public static readonly Device device = torch.device(torch.cuda.is_available() ? "cuda:0" : "cpu");
    }
}
