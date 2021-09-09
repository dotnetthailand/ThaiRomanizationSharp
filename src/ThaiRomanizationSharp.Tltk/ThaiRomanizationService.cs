using Python.Runtime;
using ThaiRomanizationSharp.Abstractions;

namespace ThaiRomanizationSharp.Tltk
{
    public class ThaiRomanizationService : IThaiRomanizationService
    {
        private readonly dynamic nlp;

        public ThaiRomanizationService()
        {
            PythonEngine.Initialize();
            // Add a path to your Python file as a searched module path
            dynamic os = Py.Import("os");
            dynamic sys = Py.Import("sys");
            var currentWorkingDirectory = os.getcwd();
            sys.path.append(currentWorkingDirectory);

            // https://pypi.org/project/tltk/#:~:text=pip%20install-,tltk,-Copy%20PIP%20instructions
            nlp = Py.Import("nlp");
        }

        public string Romanize(string inputThaiText) => nlp.th2roman(inputThaiText);

        public void Dispose() => PythonEngine.Shutdown();
    }
}
