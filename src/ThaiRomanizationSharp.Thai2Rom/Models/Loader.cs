using System;
using System.IO;
using System.Text.Json;

namespace ThaiRomanizationSharp.Thai2Rom.Models
{
    /// <summary>
    /// In the original python, this Loader was a fancy class that stored models in a local
    /// database, and could download models from the Internet. We're not that fancy.
    /// </summary>
    internal static class Loader
    {
        private const string ModelParameterPath = "./Models/Data/model_parameters.json";

        public static ModelParameters LoadParameters()
        {
            var parameters = JsonSerializer.Deserialize<ModelParameters>(
                File.ReadAllText(ModelParameterPath)
            );

            return parameters is not null
                ? parameters
                : throw new InvalidOperationException($"Unable to load required {ModelParameterPath}");
        }
    }
}
