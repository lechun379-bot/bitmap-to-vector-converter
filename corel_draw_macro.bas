Option Explicit

' CorelDRAW VBA macro
' This macro opens a bitmap in CorelDRAW, calls a Python script,
' then imports the generated SVG back into the document.

Sub ConvertBitmapToVector()
    Dim doc As Document
    Dim s As Shape
    Dim bmpPath As String
    Dim svgPath As String
    Dim pyScript As String
    Dim pythonExe As String
    Dim cmd As String
    Dim result As Long
    Dim msg As String

    Set doc = ActiveDocument
    If doc Is Nothing Then
        MsgBox "No CorelDRAW document is active."
        Exit Sub
    End If

    ' Select the first bitmap in the document.
    Set s = doc.ActivePage.SelectShapes(2)
    ' Note: CorelDRAW's object type selection is not always straightforward.
    ' For a more robust solution, the user can select the bitmap manually first.
    If s Is Nothing Then
        MsgBox "Please select a bitmap object before running this macro.", vbExclamation
        Exit Sub
    End If

    If s.Type <> cdrBitmapShape Then
        MsgBox "Selected object is not a bitmap. Please select a bitmap first.", vbExclamation
        Exit Sub
    End If

    ' Define paths.
    bmpPath = Environ$("TEMP") & "\corel_bitmap_input.png"
    svgPath = Environ$("TEMP") & "\corel_vector_output.svg"
    pyScript = Environ$("USERPROFILE") & "\Desktop\corel_vectorize.py"

    ' Export the selected bitmap to a temporary PNG file.
    s.Export bmpPath, cdrPNG

    ' Find Python executable.
    pythonExe = FindPythonExecutable()
    If pythonExe = "" Then
        MsgBox "Python was not found. Please install Python and make sure it is on PATH.", vbCritical
        Exit Sub
    End If

    ' Build command to run the Python vectorizer.
    cmd = """" & pythonExe & """ """ & pyScript & """ """ & bmpPath & """ """ & svgPath & """ --threshold 160 --blur 2 --min-area 5 --simplify 0.002 --adaptive --bezier --curves"
    result = Shell(cmd, vbHide)

    ' Wait briefly for Python to process the file.
    Dim startTime As Single
    startTime = Timer
    Do While Timer < startTime + 10
        If Dir$(svgPath) <> "" Then Exit Do
        DoEvents
    Loop

    If Dir$(svgPath) = "" Then
        MsgBox "The vector conversion process did not create the SVG file. Check the Python script path and parameters.", vbCritical
        Exit Sub
    End If

    ' Import the generated SVG into CorelDRAW.
    doc.Import svgPath

    MsgBox "Bitmap converted to SVG successfully and imported into the CorelDRAW document."
End Sub

Private Function FindPythonExecutable() As String
    Dim pathValue As String
    Dim paths() As String
    Dim i As Integer
    Dim candidate As String

    pathValue = Environ$("PATH")
    paths = Split(pathValue, ";")

    For i = 0 To UBound(paths)
        candidate = Trim$(paths(i))
        If candidate <> "" Then
            If Dir$(candidate & "\python.exe") <> "" Then
                FindPythonExecutable = candidate & "\python.exe"
                Exit Function
            End If
            If Dir$(candidate & "\python3.exe") <> "" Then
                FindPythonExecutable = candidate & "\python3.exe"
                Exit Function
            End If
        Next i
    Next i

    ' Fallback for common installation paths.
    If Dir$("C:\Python311\python.exe") <> "" Then
        FindPythonExecutable = "C:\Python311\python.exe"
        Exit Function
    End If
    If Dir$("C:\Python310\python.exe") <> "" Then
        FindPythonExecutable = "C:\Python310\python.exe"
        Exit Function
    End If
    If Dir$("C:\Python39\python.exe") <> "" Then
        FindPythonExecutable = "C:\Python39\python.exe"
        Exit Function
    End If

    FindPythonExecutable = ""
End Function
