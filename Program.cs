using System;
using System.Diagnostics;
using Python.Runtime;

namespace ThaiRomanizationSharp
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var stopWatch = new Stopwatch();
            stopWatch.Start();

            PythonEngine.Initialize();

            // Add a path to your Python file as a searched module path
            dynamic os = Py.Import("os");
            dynamic sys = Py.Import("sys");
            sys.path.append(os.getcwd());

            // https://pypi.org/project/tltk/#:~:text=pip%20install-,tltk,-Copy%20PIP%20instructions
            dynamic nlp = Py.Import("nlp");
            var roman = nlp.th2roman("ขอบคุณทุกอย่าง จ๊ะ");
            Console.WriteLine(roman);

            stopWatch.Stop();
            // Get the elapsed time as a TimeSpan value.
            var elapsedTime = stopWatch.Elapsed;
            Console.WriteLine(
                "Execution time: {0:00}:{1:00}:{2:00}.{3:00}",
                elapsedTime.Hours,
                elapsedTime.Minutes,
                elapsedTime.Seconds,
                elapsedTime.Milliseconds
            );

            PythonEngine.Shutdown();
        }
    }
}
