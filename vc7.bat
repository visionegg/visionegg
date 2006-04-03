rem Modified from http://www.vrplumber.com/programming/mstoolkit/

rem vc7.bat, copied to the command path for the machine
@echo off

Set PATH=C:\Program Files\Microsoft Visual C++ Toolkit 2003\bin;C:\Program Files\Microsoft Platform SDK for Windows Server 2003 R2\Bin;%PATH%
Set INCLUDE=C:\Program Files\Microsoft Visual C++ Toolkit 2003\include;C:\Program Files\Microsoft Platform SDK for Windows Server 2003 R2\include;%INCLUDE%
Set LIB=C:\Program Files\Microsoft Visual Studio .NET 2003\Vc7\lib;C:\Program Files\Microsoft Visual C++ Toolkit 2003\lib;C:\Program Files\Microsoft Platform SDK for Windows Server 2003 R2\Lib;%LIB%

echo Visit http://msdn.microsoft.com/visualc/using/documentation/default.aspx for
echo complete compiler documentation.