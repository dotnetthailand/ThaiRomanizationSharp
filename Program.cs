using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using Python.Included;
using Python.Runtime;

namespace ThaiLanguageToolkit
{
    class Program
    {
        static async Task Main(string[] args)
        {
            var stopWatch = new Stopwatch();
            stopWatch.Start();

            // This example demonstrates how Python.Included is able to automatically install a minimal Python
            // environment which it includes as an embedded resource in its .NET assembly file
            // Python.Included is currently fixed to Python 3.7.3 amd64 for windows
            // If you need a different Python version or platform check out the Python.Installer examples!

            // Install to local directory
            Installer.InstallPath = Path.GetFullPath(".");

            // See what the installer is doing
            Installer.LogMessage += Console.WriteLine;

            // Install the embedded python distribution
            await Installer.SetupPython();

            // Install pip3 for package installation
            Installer.TryInstallPip();

            // Use pythonnet from that installation
            PythonEngine.Initialize();

            dynamic os = Py.Import("os");
            dynamic sys = Py.Import("sys");
            sys.path.append(os.getcwd());

            //https://pypi.org/project/tltk/#:~:text=pip%20install-,tltk,-Copy%20PIP%20instructions
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
        }
    }
}
