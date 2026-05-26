Option Compare Database
Option Explicit

'中止ボタン
Private Sub btnCancel_Click()
    Call DispInit(True)
    SubFrmInit
    Me.cboKibanA.SetFocus
    Me.Refresh
End Sub

'全て返却ボタン
Private Sub btnHenkyakuAll_Click()
    Dim strSQL As String
    
    If IsNull(Me.txtCaseNo) Then
        MsgBox "返却ケースNoが入力されていません", vbCritical + vbOKOnly, "確認"
        Me.txtCaseNo.SetFocus
        Exit Sub
    End If
    
    If Me.f_返却のサブフォーム.Form.Recordset.RecordCount = 0 Then
        MsgBox "返却の対象品がありません", vbCritical + vbOKOnly, "確認"
        Me.cboKibanA.SetFocus
        Exit Sub
    End If
    
    If MsgBox("全て返却しますか？", vbQuestion + vbYesNo, "確認") <> vbYes Then
        Me.cboKibanA.SetFocus
        Exit Sub
    End If
    
    DoCmd.SetWarnings False
    
    strSQL = "UPDATE t_貸出 SET "
    strSQL = strSQL & "返却日 = #" & Me.txtHizuke & "#, "
    strSQL = strSQL & "機番 = '返-" & Me.txtCaseNo & "' "
    strSQL = strSQL & "WHERE 機番 = '" & Me.txtKiban & "' "
    strSQL = strSQL & "AND 返却日 IS NULL;"
    DoCmd.RunSQL strSQL
    
    DoCmd.SetWarnings True
    
    Call DispInit(True)
    SubFrmInit
    Me.Refresh
    MsgBox "返却処理しました", vbInformation + vbOKOnly, "確認"
End Sub

'個別返却ボタン
Private Sub btnHenkyakuOne_Click()
    Dim strSQL As String

    If IsNull(Me.txtSize) Then
        MsgBox "返却品の指定がありません", vbCritical + vbOKOnly, "確認"
        Me.cboKibanA.SetFocus
        Exit Sub
    End If
    
    If IsNull(Me.txtCaseNo) Then
        MsgBox "返却ケースNoが入力されていません", vbCritical + vbOKOnly, "確認"
        Me.txtCaseNo.SetFocus
        Exit Sub
    End If
    
    If MsgBox("個別返却しますか？", vbQuestion + vbYesNo, "確認") <> vbYes Then
        Me.cboKibanA.SetFocus
        Exit Sub
    End If
    
    DoCmd.SetWarnings False
    
    strSQL = "UPDATE t_貸出 SET "
    strSQL = strSQL & "返却日 = #" & Me.txtHizuke & "#, "
    strSQL = strSQL & "機番 = '返-" & Me.txtCaseNo & "' "
    strSQL = strSQL & "WHERE ID = " & Me.txtID & ";"
    DoCmd.RunSQL strSQL
    
    DoCmd.SetWarnings True
    
    Call DispInit(False)
    Me.Refresh
    Me.cboKibanA.SetFocus
    MsgBox "返却処理しました", vbInformation + vbOKOnly, "確認"
End Sub

'検索ボタン
Private Sub btnKensaku_Click()
    Dim strSQL As String
    
    strSQL = "SELECT t_貸出.ID, t_貸出.サイズ, t_貸出.担当者ID, t_担当者マスタ.担当者名, t_貸出.機番, "
    strSQL = strSQL & "t_貸出.貸出日, t_貸出.返却日, t_PGマスタ.ケースNo "
    strSQL = strSQL & "FROM (t_貸出 LEFT JOIN t_担当者マスタ ON t_貸出.担当者ID = t_担当者マスタ.担当者ID) "
    strSQL = strSQL & "LEFT JOIN t_PGマスタ ON t_貸出.サイズ = t_PGマスタ.サイズ "
    strSQL = strSQL & "WHERE t_貸出.機番 = '" & Me.txtKiban & "' "
    strSQL = strSQL & "AND t_貸出.完了フラグ IS NULL AND t_貸出.返却日 IS NULL "
    strSQL = strSQL & "ORDER BY t_貸出.サイズ;"
    Me.f_返却のサブフォーム.Form.RecordSource = strSQL
    
    Call DispInit(False)
    Me.txtCaseNo.SetFocus
    Me.Refresh
End Sub

'画面初期化
Private Sub DispInit(pMode As Boolean)
    Me.txtSize = Null
    Me.txtID = Null
    If pMode Then
        Me.cboKibanA = Null
        Me.cboKibanN = Null
        Me.txtKiban = Null
        Me.txtHizuke = Null
    End If
End Sub

'機番アルファベットが更新された
Private Sub cboKibanA_AfterUpdate()
    SetKiban
    If Me.cboKibanA = "数値" Then
        Me.btnKensaku.SetFocus
    Else
        Me.cboKibanN.SetFocus
    End If
    Me.txtHizuke = Format(Now(), "yyyy/mm/dd")
End Sub

'機番数字が更新された
Private Sub cboKibanN_AfterUpdate()
    SetKiban
    Me.btnKensaku.SetFocus
End Sub

'機番をセット
Private Sub SetKiban()
    If Me.cboKibanA = "数値" Then
        Me.cboKibanN = Null
        Me.cboKibanN.Enabled = False
        Me.txtKiban = "数値"
        Me.btnHenkyakuAll.Enabled = False
    Else
        Me.txtKiban = Me.cboKibanA & "-" & Me.cboKibanN
        Me.cboKibanN.Enabled = True
        Me.btnHenkyakuAll.Enabled = True
    End If
End Sub

'フォームを開く時
Private Sub Form_Open(Cancel As Integer)
    Me.f_返却のサブフォーム.Form.サイズ.ColumnWidth = 567 * 4
    Me.f_返却のサブフォーム.Form.担当者名.ColumnWidth = 567 * 2.5
    Me.f_返却のサブフォーム.Form.機番.ColumnWidth = 567 * 2
    Me.f_返却のサブフォーム.Form.貸出日.ColumnWidth = 567 * 2.4
    Me.f_返却のサブフォーム.Form.ケースNo.ColumnWidth = 567 * 1.7
    Me.f_返却のサブフォーム.Form.ID.ColumnHidden = True
    Me.f_返却のサブフォーム.Form.担当者ID.ColumnHidden = True
    Me.f_返却のサブフォーム.Form.返却日.ColumnHidden = True

    SubFrmInit
End Sub

'サブフォーム初期化
Private Sub SubFrmInit()
    Dim strSQL As String

    strSQL = "SELECT t_貸出.ID, t_貸出.サイズ, t_貸出.担当者ID, t_担当者マスタ.担当者名, t_貸出.機番, "
    strSQL = strSQL & "t_貸出.貸出日, t_貸出.返却日, t_PGマスタ.ケースNo "
    strSQL = strSQL & "FROM (t_貸出 LEFT JOIN t_担当者マスタ ON t_貸出.担当者ID = t_担当者マスタ.担当者ID) "
    strSQL = strSQL & " LEFT JOIN t_PGマスタ ON t_貸出.サイズ = t_PGマスタ.サイズ "
    strSQL = strSQL & "WHERE t_貸出.サイズ = 'ZZZZZ';"
    Me.f_返却のサブフォーム.Form.RecordSource = strSQL
    Me.Refresh
End Sub

'返却ケースNoが更新された
Private Sub txtCaseNo_AfterUpdate()
    If Len(Me.txtCaseNo) > 2 Then
        MsgBox "返却ケースNoは2桁以内にしてください", vbCritical + vbOKOnly, "確認"
        Me.cboKibanN.SetFocus
        Me.txtCaseNo.SetFocus
        Exit Sub
    End If
        
    If Me.txtKiban <> "数値" Then Me.btnHenkyakuAll.SetFocus
End Sub
