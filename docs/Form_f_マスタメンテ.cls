Option Compare Database
Option Explicit

'閉じるボタン
Private Sub btnClose_Click()
    DoCmd.Close acForm, "f_マスタメンテ"
End Sub

'削除ボタン
Private Sub btnDelete_Click()
    Dim strSQL As String
    
    If MsgBox("このサイズを削除しますか？", vbQuestion + vbYesNo, "確認") <> vbYes Then Exit Sub

    strSQL = "DELETE FROM t_PGマスタ "
    strSQL = strSQL & "WHERE サイズ = '" & Me.txtSize & "';"
    
    DoCmd.SetWarnings False
    DoCmd.RunSQL strSQL
    DoCmd.SetWarnings True
    
    MsgBox "削除しました", vbInformation + vbOKOnly, "確認"
    Forms("f_Main").Refresh
    
    DoCmd.Close acForm, "f_マスタメンテ"
End Sub

'登録ボタン
Private Sub btnTouroku_Click()
    Dim strSQL As String
    
    If IsNull(Me.txtSize) Or IsNull(Me.txtHoyuusuu) Or IsNull(Me.txtCaseNo) Then
        MsgBox "サイズ・保有数・ケースNo は必ず入力してください", vbCritical + vbOKOnly, "確認"
        Exit Sub
    ElseIf IsNumeric(Me.txtSize) And Len(Mid(Me.txtSize, InStr(Me.txtSize, ".") + 1)) <> 3 Then
        If MsgBox("サイズは小数点以下３桁で指定してください。" & _
            vbCrLf & "このまま登録を続けますか", vbCritical + vbYesNo, "確認") <> vbYes Then
            Exit Sub
        End If
    Else
        If MsgBox("登録しますか？", vbQuestion + vbYesNo, "確認") <> vbYes Then Exit Sub
    End If
    
    If Me.txtSize.Enabled Then      '新規登録
        If Not IsNull(DLookup("サイズ", "t_PGマスタ", "サイズ = '" & Me.txtSize & "'")) Then
            MsgBox "このサイズはマスタに登録済みです", vbCritical + vbOKOnly, "確認"
            Exit Sub
        End If
        strSQL = "INSERT INTO t_PGマスタ ( サイズ, 保有数, ケースNo ) VALUES ( "
        strSQL = strSQL & "'" & Me.txtSize & "', "
        strSQL = strSQL & Me.txtHoyuusuu & ", "
        strSQL = strSQL & "'" & Me.txtCaseNo & "');"
    Else
        strSQL = "UPDATE t_PGマスタ SET "
        strSQL = strSQL & "保有数 = " & Me.txtHoyuusuu & ", "
        strSQL = strSQL & "ケースNo = '" & Me.txtCaseNo & "' "
        strSQL = strSQL & "WHERE サイズ = '" & Me.txtSize & "';"
    End If
    
    DoCmd.SetWarnings False
    DoCmd.RunSQL strSQL
    DoCmd.SetWarnings True
    
    MsgBox "登録しました", vbInformation + vbOKOnly, "確認"
    Forms("f_Main").Refresh
    
    DoCmd.Close acForm, "f_マスタメンテ"
End Sub

'フォームを開く時
Private Sub Form_Open(Cancel As Integer)
    If Me.OpenArgs = "New" Then
        Me.btnDelete.Enabled = False
        Me.txtSize.Enabled = True
    Else
        Me.btnDelete.Enabled = True
        Me.txtSize.Enabled = False
        With MastData
            Me.txtSize = .sSize
            Me.txtHoyuusuu = .iSuu
            Me.txtCaseNo = .sCaseNo
        End With
    End If
End Sub

'ケースNoが更新された
Private Sub txtCaseNo_AfterUpdate()
    Me.txtCaseNo = UCase(Me.txtCaseNo)
End Sub

'サイズが更新された
Private Sub txtSize_AfterUpdate()
    Me.txtSize = UCase(Me.txtSize)
End Sub