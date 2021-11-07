$libraryName = "ThaiRomanizationSharp.Thai2Rom.ConsoleApp"
$outputDir = Join-Path -Path $PSScriptRoot -ChildPath "bin/Debug/net5.0"
$exePath = Join-Path -Path $outputDir -ChildPath "$libraryName.exe"
$exePath

& $exePath

#$alc = New-Object -TypeName System.Runtime.Loader.AssemblyLoadContext -ArgumentList "MyTest", $true
#$asm = $alc.LoadFromAssemblyPath($assemblyPath)
# $asm.GetTypes() | % { $_.FullName }

# $instance = $asm.CreateInstance("ThaiRomanizationSharp.Thai2Rom.Thai2RomService");
# $instance

# #$romanized = $instance.GetType().GetMethod("Romanize").Invoke($instance, @("นะจ๊ะ"));
# #$romanized

#$alc.Unload()




