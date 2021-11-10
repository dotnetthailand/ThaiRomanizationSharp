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
            //Wait for debugging Console.ReadKey();

            foreach (var filePath in filePaths)
            {
                var tagFile = TagLib.File.Create(filePath);
                string title = tagFile.Tag.Title;
                TimeSpan duration = tagFile.Properties.Duration;
                Console.WriteLine("Title: {0}, duration: {1}", title, duration);

                var titleCharacter = title.ToCharArray();
                titleCharacter[0] = char.ToUpper(titleCharacter[0]);

                // change title in the file
                // tagFile.Tag.Title = service.Romanize(title);
                tagFile.Tag.Title = new string(titleCharacter);
                tagFile.Save();
            }
        }
    }
}
