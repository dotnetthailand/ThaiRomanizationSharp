using System;

namespace ThaiRomanizationSharp.Abstractions
{
    /// <summary>
    /// Romanization (transliteration to English-character pronunciation) of Thai words.
    /// </summary>
    public interface IThaiRomanizationService : IDisposable
    {
        /// <summary>"Romanizes" input Thai text to English pronunciation</summary>
        /// <param name="text">Thai text to be romanized</param>
        /// <returns>English (more or less) text that spells out how the Thai text should be pronounced.</returns>
        string Romanize(string text);
    }
}
