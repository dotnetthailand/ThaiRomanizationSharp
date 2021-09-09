using System;
using Xunit;

namespace ThaiRomanizationSharp.Thai2Rom.Test
{
    public sealed class ThaiRomanizationServiceTest : IDisposable
    {
        private readonly Thai2RomService thai2RomService;

        public ThaiRomanizationServiceTest() =>
            this.thai2RomService = new Thai2RomService();

        [Theory]
        // simple thai
        [InlineData("สวัสดี", "sawatdi")]
        [InlineData("นะจ๊ะ", "nacha")]
        [InlineData("ไม่รู้ ไม่รู้", "mairu mairu")]
        // thai intermixed with other languages. Should leave the other languages alone.
        [InlineData("สวัสดี Hello こんにちは สวัสดีตอนเย็น", "sawatdi Hello こんにちは sawatditonyen")]
        // misc weird characters shouldn't be touched and shouldn't crash.
        [InlineData(" (╯°□°)╯︵ ┻━┻ สวัสดี 😀. 😃. 😄 ", " (╯°□°)╯︵ ┻━┻ sawatdi 😀. 😃. 😄 ")]
        public void Romanize_ValidInput_ReturnsRomanizedText(string thai, string expectedRomanized)
        {
            var romanized = thai2RomService.Romanize(thai);
            Assert.Equal(expectedRomanized, romanized);
        }

        [Fact]
        public void Romanize_NullInput_Throws()
        {
            Assert.Throws<ArgumentNullException>(() =>
            {
                _ = thai2RomService.Romanize(null);
            });
        }

        [Fact]
        public void Romanize_EmptyInput_ReturnsEmpty()
        {
            var romanized = thai2RomService.Romanize(string.Empty);
            Assert.Empty(romanized);
        }

        public void Dispose() =>
            this.thai2RomService.Dispose();
    }
}
