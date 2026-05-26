Option Compare Database
Option Explicit

'サイズがクリックされた
Private Sub サイズ_Click()
    With MastData
        .sSize = Me.サイズ
        .iSuu = Me.保有数
        .sCaseNo = Nz(Me.ケースNo, "")
    End With
    DoCmd.OpenForm "f_マスタメンテ", , , , , acDialog
End Sub