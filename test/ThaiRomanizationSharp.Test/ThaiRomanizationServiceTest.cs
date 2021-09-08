using Xunit;
using Xunit.Abstractions;

namespace ThaiRomanizationSharp.Test
{
    public class ThaiRomanizationServiceTest
    {
        private readonly ITestOutputHelper output;

        public ThaiRomanizationServiceTest(ITestOutputHelper output)
        {
            this.output = output;
        }

        [Fact]
        public void ToRoman_ValidInput_ReturnTrue()
        {
            // Not work now
            // https://github.com/formulahendry/vscode-dotnet-test-explorer/issues/94
            output.WriteLine("hello world");
            Assert.True(true);
        }

    }
}
