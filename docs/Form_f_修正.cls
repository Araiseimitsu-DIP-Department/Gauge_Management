Option Compare Database
Option Explicit

'閉じるボタン
Private Sub btnClose_Click()
    DoCmd.Close acForm, "f_修正"
End Sub

'削除ボタン
Private Sub btnSakujo_Click()
    Dim strSQL As String

    If MsgBox("削除しますか？", vbQuestion + vbYesNo, "確認") <> vbYes Then
        Me.txtHizuke.SetFocus
        Exit Sub
    End If
    
    DoCmd.SetWarnings False
    strSQL = "DELETE FROM t_貸出 "
    strSQL = strSQL & "WHERE ID =" & GaugeData.ID & ";"
    DoCmd.RunSQL strSQL
    DoCmd.SetWarnings True
    
    DoCmd.Close acForm, "f_修正"
    Forms("f_Main").Refresh
End Sub

'修正ボタン
Private Sub btnShuusei_Click()
    Dim strSQL As String
    Dim ErrFlg As Boolean
    
    ErrFlg = False
    If IsNull(Me.txtHizuke) Then ErrFlg = True
    If IsNull(Me.txtKiban) Then ErrFlg = True
    If IsNull(Me.cboTantou) Then ErrFlg = True
    If IsNull(Me.txtSize) Then ErrFlg = True
    If ErrFlg Then
        MsgBox "未入力の項目があります。確認してください", vbCritical + vbOKOnly, "確認"
        Me.txtHizuke.SetFocus
        Exit Sub
    End If
    
    If MsgBox("修正しますか？", vbQuestion + vbYesNo, "確認") <> vbYes Then
        Me.txtHizuke.SetFocus
        Exit Sub
    End If
    
    DoCmd.SetWarnings False
    strSQL = "UPDATE t_貸出 SET "
    strSQL = strSQL & "貸出日 = #" & Me.txtHizuke & "#, "
    strSQL = strSQL & "機番 = '" & Me.txtKiban & "', "
    strSQL = strSQL & "担当者ID = '" & Me.cboTantou & "', "
    strSQL = strSQL & "サイズ = '" & Me.txtSize & "' "
    strSQL = strSQL & "WHERE ID =" & GaugeData.ID & ";"
    DoCmd.RunSQL strSQL
    DoCmd.SetWarnings True
    
    DoCmd.Close acForm, "f_修正"
    Forms("f_Main").Refresh
End Sub

'フォームを開く時
Private Sub Form_Open(Cancel As Integer)
    With GaugeData
        Me.txtHizuke = .Hizuke
        Me.txtKiban = .Kiban
        Me.cboTantou = .TantouCD
        Me.txtSize = .GaugeSize
    End With
End Sub