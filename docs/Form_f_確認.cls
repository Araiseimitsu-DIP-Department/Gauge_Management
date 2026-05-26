Option Compare Database
Option Explicit

'中止ボタン
Private Sub btnCancel_Click()
    If MsgBox("中止しますか？", vbQuestion + vbYesNo, "確認") <> vbYes Then
        Me.txtCaseNo.SetFocus
        Exit Sub
    End If
    
    Me.txtCaseNo = Null
    SubFrmInit
    Me.txtID = Null
    Me.txtSize = Null
    Me.txtCaseNo.SetFocus
    Me.Refresh
End Sub

'チェックボタン
Private Sub btnCheck_Click()
    Dim strSQL As String

    strSQL = "SELECT DISTINCT t_貸出.返却日, t_貸出.機番 FROM t_貸出 "
    strSQL = strSQL & "WHERE (t_貸出.完了フラグ Is Null) AND (Not t_貸出.返却日 Is Null);"
    Me.f_確認のサブフォーム2.Form.RecordSource = strSQL
    Me.Refresh
    Me.txtCaseNo.SetFocus
End Sub

'全て確認ボタン
Private Sub btnKakunin_Click()
    Dim strSQL As String

    If MsgBox("確認処理を行いますか？", vbQuestion + vbYesNo, "確認") <> vbYes Then
        Me.txtCaseNo.SetFocus
        Exit Sub
    End If
    
    DoCmd.Echo False
    DoCmd.SetWarnings False
    
    With Me.f_確認のサブフォーム.Form.Recordset
        .MoveFirst
        Do While Not .EOF
            strSQL = "UPDATE t_貸出 SET 完了フラグ = 'Y' "
            strSQL = strSQL & "WHERE ID = " & .Fields("ID") & ";"
            DoCmd.RunSQL strSQL
            .MoveNext
        Loop
        .MoveFirst
    End With
    
    DoCmd.SetWarnings True
    DoCmd.Echo True
    
    SubFrmInit
    Me.txtCaseNo = Null
    Me.txtID = Null
    Me.txtSize = Null
    Me.txtCaseNo.SetFocus
    Me.Refresh
    
    MsgBox "確認しました。", vbInformation + vbOKOnly, "確認"
End Sub

'個別確認ボタン
Private Sub btnKakuninOne_Click()
    Dim strSQL As String

    If IsNull(Me.txtSize) Then
        MsgBox "個別確認サイズの指定がありません", vbCritical + vbOKOnly, "確認"
        Me.txtCaseNo.SetFocus
        Exit Sub
    End If
    
    If MsgBox("個別確認処理を行いますか？", vbQuestion + vbYesNo, "確認") <> vbYes Then
        Me.txtCaseNo.SetFocus
        Exit Sub
    End If
    
    DoCmd.SetWarnings False
    
    strSQL = "UPDATE t_貸出 SET 完了フラグ = 'Y' "
    strSQL = strSQL & "WHERE ID = " & Me.txtID & ";"
    DoCmd.RunSQL strSQL
    
    DoCmd.SetWarnings True
    
    Me.txtID = Null
    Me.txtSize = Null
    Me.txtCaseNo.SetFocus
    Me.Refresh
    
    MsgBox "個別確認しました。", vbInformation + vbOKOnly, "確認"
End Sub

'検索ボタン
Private Sub btnKensaku_Click()
    Dim strSQL As String
    
    strSQL = "SELECT t_貸出.ID, t_貸出.サイズ, t_貸出.担当者ID, t_担当者マスタ.担当者名, t_貸出.機番, t_貸出.貸出日, t_貸出.返却日, "
    strSQL = strSQL & "t_PGマスタ.ケースNo "
    strSQL = strSQL & "FROM (t_貸出 LEFT JOIN t_担当者マスタ ON t_貸出.担当者ID = t_担当者マスタ.担当者ID) "
    strSQL = strSQL & "LEFT JOIN t_PGマスタ ON t_貸出.サイズ = t_PGマスタ.サイズ "
    strSQL = strSQL & "WHERE t_貸出.機番 = '返-" & Me.txtCaseNo & "' "
    strSQL = strSQL & "AND t_貸出.完了フラグ IS NULL;"
    Me.f_確認のサブフォーム.Form.RecordSource = strSQL
    
    Me.txtCaseNo.SetFocus
    Me.Refresh

End Sub

'フォーム開く時
Private Sub Form_Open(Cancel As Integer)
    Dim strSQL As String
    
    Me.f_確認のサブフォーム.Form.サイズ.ColumnWidth = 567 * 4
    Me.f_確認のサブフォーム.Form.担当者名.ColumnWidth = 567 * 2.5
    Me.f_確認のサブフォーム.Form.機番.ColumnWidth = 567 * 2
    Me.f_確認のサブフォーム.Form.返却日.ColumnWidth = 567 * 2.4
    Me.f_確認のサブフォーム.Form.ケースNo.ColumnWidth = 567 * 1.7
    
    Me.f_確認のサブフォーム.Form.ID.ColumnHidden = True
    Me.f_確認のサブフォーム.Form.担当者ID.ColumnHidden = True
    Me.f_確認のサブフォーム.Form.貸出日.ColumnHidden = True
    Me.f_確認のサブフォーム.Form.完了フラグ.ColumnHidden = True

    SubFrmInit
    
    Me.f_確認のサブフォーム2.Form.機番.ColumnWidth = 567 * 2
    Me.f_確認のサブフォーム2.Form.返却日.ColumnWidth = 567 * 2.4
    Me.f_確認のサブフォーム2.Form.完了フラグ.ColumnHidden = True
    strSQL = "SELECT DISTINCT t_貸出.返却日, t_貸出.機番 FROM t_貸出 "
    strSQL = strSQL & "WHERE t_貸出.完了フラグ = 'N';"
    Me.f_確認のサブフォーム2.Form.RecordSource = strSQL

End Sub

'サブフォーム初期化
Private Sub SubFrmInit()
    Dim strSQL As String

    strSQL = "SELECT t_貸出.ID, t_貸出.サイズ, t_貸出.担当者ID, t_担当者マスタ.担当者名, t_貸出.機番, t_貸出.貸出日, t_貸出.返却日, "
    strSQL = strSQL & "t_PGマスタ.ケースNo "
    strSQL = strSQL & "FROM (t_貸出 LEFT JOIN t_担当者マスタ ON t_貸出.担当者ID = t_担当者マスタ.担当者ID) "
    strSQL = strSQL & "LEFT JOIN t_PGマスタ ON t_貸出.サイズ = t_PGマスタ.サイズ "
    strSQL = strSQL & "WHERE t_貸出.サイズ = 'ZZZZZ';"
    Me.f_確認のサブフォーム.Form.RecordSource = strSQL
    Me.Refresh
End Sub
