using System;
using System.IO;

namespace ThaiRomanizationSharp.Thai2Rom.ConsoleApp
{
    public class Program
    {
        private static Thai2RomService service = new Thai2RomService();

        public static void Main(string[] args)
        {
            const string path = @"";
            var filePaths = Directory.GetFiles(path, "*.flac", SearchOption.AllDirectories);
            // Wait for debugging
            // Console.ReadKey();

            foreach (var filePath in filePaths)
            {
                var tagFile = TagLib.File.Create(filePath);
                var title = tagFile.Tag.Title;
                var duration = tagFile.Properties.Duration;
                Console.WriteLine("Title: {0}, duration: {1}", title, duration);

                var romanizedTitle = service.Romanize(title);
                var titleCharacter = romanizedTitle.ToCharArray();
                titleCharacter[0] = char.ToUpper(titleCharacter[0]);

                // Change title tag in the current file
                tagFile.Tag.Title = new string(titleCharacter);
                tagFile.Save();
            }
        }
    }
}
