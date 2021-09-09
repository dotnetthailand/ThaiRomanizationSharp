using Xunit;
using Xunit.Abstractions;

namespace ThaiRomanizationSharp.Test
{
    public class ThaiRomanizationServiceTest
    {
        private readonly ITestOutputHelper output;
        private readonly ThaiRomanizationService thaiRomanizationService;

        public ThaiRomanizationServiceTest(ITestOutputHelper output)
        {
            this.output = output;
            this.thaiRomanizationService = new ThaiRomanizationService();
        }

        [Theory]
        [InlineData("นะจ๊ะ", "na ca <s/>")]
        [InlineData("ไม่รู้ ไม่รู้", "mai ru <s/>mai ru <s/>")]
        public void ToRoman_ValidInput_ReturnCorrect(string inputText, string expectedOutputText)
        {
            var actualOutputText = thaiRomanizationService.ToRoman(inputText);
            // There is a output if you run a test with "Run Test" code lens but not .NET Core Test Explorer
            output.WriteLine($"expectedOutputText: {actualOutputText}");

            Assert.Equal(expectedOutputText, actualOutputText);
        }
    }
}
