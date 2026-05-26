Option Compare Database
Option Explicit

Private Sub サイズ_Click()
    Forms("f_返却").txtID = Me.ID
    Forms("f_返却").txtSize = Me.サイズ
End Sub