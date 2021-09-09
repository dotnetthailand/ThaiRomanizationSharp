# ThaiRomanizationSharp

This .NET project contains several implementations of [Romanization](https://en.wikipedia.org/wiki/Romanization) of Thai text.

For example, "สวัสดี" is "romanized" to "sawatdi"

There are currently two romanization algorithms:

1. The **Thai Language Toolkit** (TLTK) algorithm [originally from here](https://github.com/attapol/tltk).
    - This implementation invokes Python code, and requires python to be installed.
1. The **Thai2Rom** algorithm [originally from here](https://github.com/PyThaiNLP/pythainlp).
    - This implementation runs native code (using the Torch machine learning framework -- available for Mac OS / Windows / Linux). The native code for these 3 platforms is bundled in the project and no installation is required.

# Credits for Thai Language Toolkit

- Credit to [Assoc.Prof. Wirote Aroonmanakun (Ph.D.)](http://pioneer.chula.ac.th/~awirote/)
- Director of the Siridhorn Thai Language Institute, Chulalongkorn University
- Original code is from https://github.com/attapol/tltk/blob/master/tltk/nlp.py.
- Thai Romanization main project page http://pioneer.chula.ac.th/~awirote/resources/thai-romanization.html.

# Credits for Thai2Rom project

The C# code of the Thai2Rom algorithm is based on the Python code from the PyThaiNLP project.

- [Main PyThaiNLP repository](https://github.com/PyThaiNLP/pythainlp)
   - [Specific "thai2rom" algorithm that was ported](https://github.com/PyThaiNLP/pythainlp/blob/a1028b5799fd8edd7dc8118e7457a12e60ffc467/pythainlp/transliterate/thai2rom.py)
- [PyTorch Model (python pickle format)](https://raw.githubusercontent.com/artificiala/thai-romanization/master/notebook/thai2rom-pytorch-attn-v0.1.tar)
- [Training jupyter notebook](https://github.com/artificiala/thai-romanization/blob/master/notebook/thai_romanize_pytorch_seq2seq_attention.ipynb)

# How to run the project locally

1. For running the ThaiRomanizationSharp.Thai2Rom library, either reference it from your project, or run the unit tests as normal via the `dotnet` command line, Visual Studio Code, or Visual Studio.
  - See the README.md in the ThaiRomanizationSharp.Thai2Rom subdirectory for more information.
1. For running the ThaiRomanizationSharp.Thai2Rom library Thai Language Toolkit Project, there are some setup steps you need to do first. The rest of the README is devoted to these steps.
  - See the README.md in the ThaiRomanizationSharp.Tltk subdirectory for more information.

## Run the project

- In VS Code open integrated terminal by pressing **ctrl+`**.
- The terminal should start from the root of the project.
- Run the project with the following command:
  ```sh
  $ dotnet run
  ```
- Wait for a while and you should find an output message in the integrated terminal.

# Reference & useful resources

- https://github.com/PyThaiNLP/pythainlp/issues/11
- https://github.com/comdevx/thai2karaoke
- [Debugging with Code lens option](https://github.com/formulahendry/vscode-dotnet-test-explorer#debugging-alpha)
- [Not launching debugger issue](https://github.com/formulahendry/vscode-dotnet-test-explorer/issues/247)
- [XUnit.ITestOutputHelper.WriteLine not showing up issue](https://github.com/formulahendry/vscode-dotnet-test-explorer/issues/94)

# Todo

- [ ] More details what code changes in nlp.py
- [ ] Convert project to a class library
- [ ] Unit test with xUnit
- [ ] GitHub Actions to run a unit test
- [ ] GitHub Actions to deploy a library to Nuget and release page
- [ ] Custom Docker image
- [ ] Deploy example project to Azure App Service container
