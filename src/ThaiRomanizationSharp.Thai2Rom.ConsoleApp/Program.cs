using System;

namespace ThaiRomanizationSharp.Thai2Rom.ConsoleApp
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var service = new Thai2RomService();
            var output = service.Romanize("นะจ๊ะ ไม่รู้ ไม่รู้");
            Console.WriteLine(output);
        }
    }
}
