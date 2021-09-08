using Python.Runtime;

namespace ThaiRomanizationSharp
{
    public class ThaiRomanizationService
    {
        public string ToRoman(string inputThaiText)
        {
            PythonEngine.Initialize();

            // Add a path to your Python file as a searched module path
            dynamic os = Py.Import("os");
            dynamic sys = Py.Import("sys");
            sys.path.append(os.getcwd());

            // https://pypi.org/project/tltk/#:~:text=pip%20install-,tltk,-Copy%20PIP%20instructions
            dynamic nlp = Py.Import("nlp");

            var roman = nlp.th2roman(inputThaiText);
            PythonEngine.Shutdown();

            return roman;
        }
    }
}
