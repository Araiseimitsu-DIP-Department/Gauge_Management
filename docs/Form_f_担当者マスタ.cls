Option Compare Database
Option Explicit

'閉じるボタン
Private Sub btnClose_Click()
    DoCmd.Close acForm, "f_担当者マスタ"
End Sub

'フォームを閉じる時
Private Sub Form_Close()
    Forms("f_Main").Refresh
    Forms("f_Main").cboKibanA.SetFocus
End Sub

'フォームを開く時
Private Sub Form_Open(Cancel As Integer)
    Me.f_担当者マスタのサブフォーム.Form.担当者ID.ColumnWidth = 567 * 2.2
    Me.f_担当者マスタのサブフォーム.Form.担当者名.ColumnWidth = 567 * 3
    Me.f_担当者マスタのサブフォーム.Form.部署.ColumnWidth = 567 * 1.8
    Me.f_担当者マスタのサブフォーム.Form.かな.ColumnWidth = 567 * 1.8
    Me.f_担当者マスタのサブフォーム.Form.表示.ColumnWidth = 567 * 1.8
End Sub