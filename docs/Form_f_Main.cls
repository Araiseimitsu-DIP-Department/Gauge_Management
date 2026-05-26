Option Compare Database
Option Explicit

'中止ボタン
Private Sub btnCancel_Click()
    If MsgBox("入力を中止しますか？", vbQuestion + vbYesNo, "確認") = vbYes Then DispInit
    Me.cboKibanA.SetFocus
End Sub

'サブフォームクリアボタン
Private Sub btnClear_Click()
    SubFrmInit
    Me.cboKibanA.SetFocus
End Sub

'返却（画面）ボタン
Private Sub btnHenkyakuOpen_Click()
    DoCmd.OpenForm "f_返却", acNormal
    Me.cboKibanA.SetFocus
End Sub

'確認（画面）ボタン
Private Sub btnKakuninOpen_Click()
    DoCmd.OpenForm "f_確認", acNormal
    Me.cboKibanA.SetFocus
End Sub

'検索ボタン
Private Sub btnKensaku_Click()
    Dim strSQL As String
    
    strSQL = "SELECT t_貸出.ID, t_貸出.サイズ, t_貸出.担当者ID, t_担当者マスタ.担当者名, t_貸出.機番, t_貸出.貸出日, t_PGマスタ.保有数 "
    strSQL = strSQL & "FROM (t_貸出 LEFT JOIN t_担当者マスタ ON t_貸出.担当者ID = t_担当者マスタ.担当者ID) "
    strSQL = strSQL & "LEFT JOIN t_PGマスタ ON t_貸出.サイズ = t_PGマスタ.サイズ "
    If Me.fraKoumoku = 1 Then       'サイズで検索
        If IsNull(Me.txtKensakuSize) Then
            MsgBox "サイズの指定がありません", vbCritical + vbOKOnly, "確認"
            Me.txtKensakuSize.SetFocus
            Exit Sub
        End If
        If Me.chkLike Then          'から始まる
            strSQL = strSQL & "WHERE t_貸出.サイズ LIKE '" & Me.txtKensakuSize & "*' "
        Else
            strSQL = strSQL & "WHERE t_貸出.サイズ = '" & Me.txtKensakuSize & "' "
        End If
    Else
        If IsNull(Me.txtKiban) Then
            MsgBox "機番の指定がありません", vbCritical + vbOKOnly, "確認"
            Me.cboKibanA.SetFocus
            Exit Sub
        End If
        strSQL = strSQL & "WHERE t_貸出.機番 = '" & Me.txtKiban & "' "
    End If
    strSQL = strSQL & "AND t_貸出.完了フラグ IS NULL "
    strSQL = strSQL & "ORDER BY t_貸出.サイズ;"
    Me.f_Mainのサブフォーム.Form.RecordSource = strSQL
    
    Me.Refresh
End Sub

'メンテナンスボタン
Private Sub btnMainte_Click()
    DoCmd.OpenTable "t_貸出", acViewNormal
    Me.cboKibanA.SetFocus
End Sub

'マスタ検索ボタン
Private Sub btnMastKensaku_Click()
    Dim sCrt As String
    
    If IsNull(Me.txtMastSize) Then
        Me.txtMastSize.SetFocus
        Exit Sub
    End If
    
    sCrt = "サイズ = '" & Me.txtMastSize & "'"
    If Not IsNull(DLookup("サイズ", "t_PGマスタ", sCrt)) Then
        Me.f_Mainのサブフォーム2.Form.Recordset.FindFirst sCrt
    Else
        MsgBox "該当するサイズはありません", vbCritical + vbOKOnly, "確認"
    End If
End Sub

'マスタ新規ボタン
Private Sub btnMastNew_Click()
    DoCmd.OpenForm "f_マスタメンテ", , , , , acDialog, "New"
End Sub

'終了ボタン
Private Sub btnQuit_Click()
    DoCmd.Quit
End Sub

'整形ボタン
Private Sub btnSeikei_Click()
    Dim cnn As ADODB.Connection
    Dim rst As ADODB.Recordset
    Dim iPos As Integer
    Dim i As Integer
    Dim sTmp As String
    
    If MsgBox("旧貸出済みゲージの整形を行います。  実行しますか？", vbQuestion + vbYesNo, "確認") <> vbYes Then Exit Sub
    
    Set cnn = CurrentProject.Connection
    Set rst = New ADODB.Recordset
    rst.Open "t_貸出", cnn, adOpenStatic, adLockOptimistic
    
    With rst
        .MoveFirst
        Do While Not .EOF
            If IsNull(.Fields("完了フラグ")) And Len(.Fields("サイズ")) <= 6 Then
                iPos = InStr(.Fields("サイズ"), ".")
                If iPos > 0 Then
                    sTmp = .Fields("サイズ")
                    sTmp = Left(sTmp & "000", iPos + 3)
                    .Fields("サイズ") = sTmp
                    .Update
                    i = i + 1
                End If
            End If
            .MoveNext
        Loop
    End With
    
    rst.Close
    Set rst = Nothing
    Set cnn = Nothing
    
    MsgBox "終了しました：" & CStr(i), vbInformation + vbOKOnly, "確認"
    
End Sub

'担当者マスタボタン
Private Sub btnTantouM_Click()
    DoCmd.OpenForm "f_担当者マスタ", acNormal, , , , acDialog
End Sub

'登録ボタン
Private Sub btnTouroku_Click()
    Dim strSQL As String
    Dim i As Integer
    Dim ErrFlg As Boolean
    Dim CtrlName As String
    Dim iCnt As Integer
    Dim sMsg As String
    
    'エラーチェック
    ErrFlg = False
    If IsNull(Me.txtHizuke) Then ErrFlg = True
    If IsNull(Me.cboKibanA) Then ErrFlg = True
    If Me.cboKibanA <> "数値" And IsNull(Me.cboKibanN) Then ErrFlg = True
    If IsNull(Me.cboTantou) Then ErrFlg = True
    
    iCnt = 0
    For i = 1 To 20
        CtrlName = "txtGauge" & CStr(i)
        If Not IsNull(Controls(CtrlName)) Then iCnt = iCnt + 1
    Next
    If iCnt = 0 Then ErrFlg = True
    
    If ErrFlg Then
        MsgBox "必要項目が入力されていません", vbCritical + vbOKOnly, "確認"
        Me.cboKibanA.SetFocus
        Exit Sub
    End If
    
    '登録
    If MsgBox("登録しますか？", vbQuestion + vbYesNo, "確認") <> vbYes Then
        Me.cboKibanA.SetFocus
        Exit Sub
    End If
    For i = 1 To 20
        CtrlName = "txtGauge" & CStr(i)
        If Not IsNull(Controls(CtrlName)) Then Call InsData(CtrlName)
    Next
    
    strSQL = "SELECT t_貸出.ID, t_貸出.サイズ, t_貸出.担当者ID, t_担当者マスタ.担当者名, t_貸出.機番, t_貸出.貸出日, t_PGマスタ.保有数 "
    strSQL = strSQL & "FROM (t_貸出 LEFT JOIN t_担当者マスタ ON t_貸出.担当者ID = t_担当者マスタ.担当者ID) "
    strSQL = strSQL & "LEFT JOIN t_PGマスタ ON t_貸出.サイズ = t_PGマスタ.サイズ "
    strSQL = strSQL & "WHERE t_貸出.貸出日 = #" & Me.txtHizuke & "# "
    strSQL = strSQL & "AND t_貸出.機番 = '" & Me.txtKiban & "' "
    strSQL = strSQL & "AND t_貸出.担当者ID = '" & Me.cboTantou & "' "
    strSQL = strSQL & "ORDER BY t_貸出.サイズ;"
    Me.f_Mainのサブフォーム.Form.RecordSource = strSQL
    
    DispInit
    Me.Refresh
    Me.cboKibanA.SetFocus
    
    MsgBox "登録しました。内容を確認してください" & vbCrLf & _
           "確認が終わったら「一覧クリア」ボタンをクリックしてください", vbInformation + vbOKOnly, "確認"
End Sub

'機番アルファベットが更新された
Private Sub cboKibanA_AfterUpdate()
    SetKiban
    If Me.cboKibanN.Enabled Then
        Me.cboKibanN.SetFocus
    Else
        Me.cboTantou.SetFocus
    End If
    Me.txtHizuke = Format(Now(), "yyyy/mm/dd")
End Sub

'機番数字が更新された
Private Sub cboKibanN_AfterUpdate()
    SetKiban
    Me.cboTantou.SetFocus
End Sub

'機番をセット
Private Sub SetKiban()
    Dim strSQL As String
    
    strSQL = "SELECT t_担当者マスタ.担当者ID, t_担当者マスタ.担当者名 "
    strSQL = strSQL & "FROM t_担当者マスタ "
    strSQL = strSQL & "WHERE t_担当者マスタ.表示 = 'Y' "
    
    If Me.cboKibanA = "数値" Then
        Me.txtKiban = "数値"
        Me.cboKibanN = Null
        Me.cboKibanN.Enabled = False
        strSQL = strSQL & " And t_担当者マスタ.部署 = '数値' "
    Else
        Me.cboKibanN.Enabled = True
        Me.txtKiban = Me.cboKibanA & "-" & Me.cboKibanN
        If Me.txtKiban = "-" Then Me.txtKiban = Null        '両方なければNull(消された場合に対応)
        strSQL = strSQL & " And t_担当者マスタ.部署 = '製造' "
    End If
    strSQL = strSQL & "ORDER BY t_担当者マスタ.かな;"
    Me.cboTantou.RowSource = strSQL
End Sub

'担当者が更新された
Private Sub cboTantou_AfterUpdate()
    Me.txtGauge1.SetFocus
End Sub

'貸出データ作成
Private Sub InsData(pCtrl As String)
    Dim strSQL As String
    
    DoCmd.SetWarnings False
    
    strSQL = "INSERT INTO t_貸出 ( サイズ, 担当者ID, 機番, 貸出日 "
    strSQL = strSQL & ") VALUES ( "
    strSQL = strSQL & "'" & Controls(pCtrl) & "', "
    strSQL = strSQL & "'" & Me.cboTantou & "', "
    strSQL = strSQL & "'" & Me.txtKiban & "', "
    strSQL = strSQL & "#" & Me.txtHizuke & "# );"
    DoCmd.RunSQL strSQL
    
    DoCmd.SetWarnings True
End Sub

'画面初期化
Private Sub DispInit()
    Dim i As Integer
    Dim CtrlName As String
    
    Me.txtHizuke = Null
    Me.cboKibanA = Null
    Me.cboKibanN = Null
    Me.txtKiban = Null
    Me.cboTantou = Null
    
    For i = 1 To 20
        CtrlName = "txtGauge" & CStr(i)
        Controls(CtrlName) = Null
    Next
End Sub

'サブフォーム初期化
Private Sub SubFrmInit()
    Dim strSQL As String

    strSQL = "SELECT t_貸出.ID, t_貸出.サイズ, t_貸出.担当者ID, t_担当者マスタ.担当者名, t_貸出.機番, t_貸出.貸出日, t_PGマスタ.保有数 "
    strSQL = strSQL & "FROM  (t_貸出 LEFT JOIN t_担当者マスタ ON t_貸出.担当者ID = t_担当者マスタ.担当者ID) "
    strSQL = strSQL & "LEFT JOIN t_PGマスタ ON t_貸出.サイズ = t_PGマスタ.サイズ  "
    strSQL = strSQL & "WHERE t_貸出.サイズ = 'ZZZZZ';"
    Me.f_Mainのサブフォーム.Form.RecordSource = strSQL
End Sub

'フォームを開く時
Private Sub Form_Open(Cancel As Integer)
    Me.f_Mainのサブフォーム.Form.貸出日.ColumnWidth = 567 * 2.4
    Me.f_Mainのサブフォーム.Form.機番.ColumnWidth = 567 * 1.5
    Me.f_Mainのサブフォーム.Form.サイズ.ColumnWidth = 567 * 4
    Me.f_Mainのサブフォーム.Form.担当者名.ColumnWidth = 567 * 2.7
    Me.f_Mainのサブフォーム.Form.ID.ColumnHidden = True
    Me.f_Mainのサブフォーム.Form.担当者ID.ColumnHidden = True
    Me.f_Mainのサブフォーム.Form.保有数.ColumnWidth = 567 * 1.5
    
    SubFrmInit

    Me.f_Mainのサブフォーム2.Form.サイズ.ColumnWidth = 567 * 4
    Me.f_Mainのサブフォーム2.Form.保有数.ColumnWidth = 567 * 1.8
    Me.f_Mainのサブフォーム2.Form.ケースNo.ColumnWidth = 567 * 1.6


End Sub
