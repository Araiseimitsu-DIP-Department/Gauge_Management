Option Compare Database
Option Explicit

'サイズがクリックされた
Private Sub サイズ_Click()
    Forms("f_確認").txtID = Me.ID
    Forms("f_確認").txtSize = Me.サイズ
End Sub